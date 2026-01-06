import base64
import os
from PIL import Image
import numpy as np
import textwrap
# steganography_detector.py
from stegano import lsb
import subprocess
import requests
import os

class SteganographyDetector:
    def __init__(self):
        self.binwalk_available = self._check_binwalk()
        self.stegdetect_available = self._check_stegdetect()
    
    def _check_binwalk(self):
        """Check if binwalk is available"""
        try:
            result = subprocess.run(['which', 'binwalk'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_stegdetect(self):
        """Check if stegdetect is available"""
        try:
            result = subprocess.run(['which', 'stegdetect'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    # def stegano_lsb(self, image_path):
    #     """LSB steganography detection"""
    #     try:
    #         if not os.path.exists(image_path):
    #             return {'found': False, 'error': 'File not found'}
            
    #         # Check if file is a valid image
    #         from PIL import Image
    #         try:
    #             with Image.open(image_path) as img:
    #                 img.verify()
    #         except Exception as e:
    #             return {'found': False, 'error': f'Invalid image file: {str(e)}'}
            
    #         hidden = lsb.reveal(image_path)
    #         if hidden:
    #             return {'found': True, 'data': hidden}
    #         else:
    #             return {'found': False, 'data': 'No hidden data found'}
    #     except Exception as e:
    #         return {'found': False, 'error': str(e)}
 # Robust appended-data scanner + manual LSB extractor

# --- paste this inside the SteganographyDetector class ---

# add at the top of the file if not present

    def find_appended_signatures(self, filepath):
        """
        Return a list of findings for appended data after EOF markers.
        Each finding is a dict:
        {'marker': name, 'marker_offset': idx, 'appended_len': n,
        'embedded_signatures': [ { 'type': 'JPEG', 'sig_offset': pos, 'abs_offset': abs_pos,
                                    'length': length, 'data_b64': '...' }, ... ]
        }
        NOTE: data_b64 contains the carved bytes (base64 encoded) for the embedded signature.
        """
        findings = []
        try:
            with open(filepath, "rb") as f:
                data = f.read()
        except Exception as e:
            return {'error': f'cannot read file: {e}'}

        markers = {
            "JPEG_EOI": b"\xff\xd9",
            "PNG_IEND": b"IEND\xaeB`\x82",
            "GIF_TERMINATOR": b";"
        }
        sigs = {
            b"PK\x03\x04": "ZIP",
            b"%PDF": "PDF",
            b"\x89PNG": "PNG",
            b"\xff\xd8": "JPEG",
            b"Rar!": "RAR",
            b"7z\xbc\xaf\x27\x1c": "7Z"
        }

        for name, sig in markers.items():
            idx = data.find(sig)
            if idx != -1:
                start = idx + len(sig)
                appended_len = max(0, len(data) - start)
                entry = {'marker': name, 'marker_offset': idx, 'appended_len': appended_len, 'embedded_signatures': []}
                if start < len(data):
                    appended = data[start:]
                    for sbytes, sname in sigs.items():
                        pos = appended.find(sbytes)
                        if pos != -1:
                            abs_pos = start + pos
                            # carve heuristics: for JPEG, try to find EOI; otherwise return from sig to end
                            if sbytes == b"\xff\xd8":
                                end = data.find(b"\xff\xd9", abs_pos)
                                if end != -1:
                                    end += 2
                                else:
                                    end = len(data)
                            else:
                                end = len(data)
                            carved = data[abs_pos:end]
                            entry['embedded_signatures'].append({
                                'type': sname,
                                'sig_offset_in_appended': pos,
                                'abs_offset': abs_pos,
                                'length': len(carved),
                                'data_b64': base64.b64encode(carved).decode('ascii')
                            })
                findings.append(entry)
        return findings


    def manual_lsb_extract(self, filepath, lsb_bits=1, channels=(0,1,2), max_bytes=None):
        """
        Extract LSB stream from image (RGB conversion).
        Returns dict: {'bytes_b64': base64str, 'bytes_len': n, 'printable_ratio': r, 'sample_text': '...'}
        Does NOT write to disk.
        """
        try:
            img = Image.open(filepath)
        except Exception as e:
            return {'error': f'cannot open image: {e}'}

        rgb = img.convert("RGB")
        arr = np.array(rgb)
        h, w, c = arr.shape

        bits = []
        for y in range(h):
            for x in range(w):
                for ch in channels:
                    val = int(arr[y, x, ch])
                    # extract lsb_bits LSBs (least-significant first)
                    for i in range(lsb_bits):
                        bits.append(str((val >> i) & 1))

        # convert bits -> bytes
        bstr = "".join(bits)
        extra = (-len(bstr)) % 8
        if extra:
            bstr += "0" * extra
        out = bytearray()
        for i in range(0, len(bstr), 8):
            out.append(int(bstr[i:i+8], 2))
            if max_bytes and len(out) >= max_bytes:
                break

        bbytes = bytes(out)
        printable = sum(32 <= bb < 127 or bb in (9,10,13) for bb in bbytes) / max(1, len(bbytes))
        sample = bbytes[:512].rstrip(b"\x00\r\n\t ").decode('utf-8', errors='replace')

        return {
            'bytes_b64': base64.b64encode(bbytes).decode('ascii'),
            'bytes_len': len(bbytes),
            'printable_ratio': printable,
            'sample_text': sample
        }


    def scan_for_ascii_runs(self, data_bytes, min_len=30):
        """
        Helper: scan an in-memory bytes object for long ASCII runs.
        Returns list of found runs as strings.
        """
        runs = []
        cur = bytearray()
        for b in data_bytes:
            if 32 <= b < 127 or b in (9,10,13):
                cur.append(b)
            else:
                if len(cur) >= min_len:
                    runs.append(cur.decode('utf-8', errors='replace'))
                cur = bytearray()
        if len(cur) >= min_len:
            runs.append(cur.decode('utf-8', errors='replace'))
        return runs


    def stegano_lsb(self, image_path):
        """
        Unified LSB detector with friendlier heuristics:
        - Try stegano.lsb.reveal() safely (records error if it fails)
        - Always run manual LSB fallback (RGB conversion)
        - Uses looser heuristics to detect short/padded text payloads
        Returns dict: {'found', 'method', 'data_preview', 'score', 'data_b64', 'error'}
        """
        res = {'found': False, 'method': None, 'data_preview': None, 'score': 0.0, 'data_b64': None, 'error': None}

        # 1) Try stegano.lsb.reveal safely
        try:
            from stegano import lsb as steg_lsb
            try:
                hidden = steg_lsb.reveal(image_path)
                if hidden:
                    res.update({'found': True, 'method': 'stegano.lsb', 'data_preview': str(hidden)[:512]})
                    return res
            except Exception as e:
                # record error but do NOT return; proceed to manual fallback
                res['error'] = f"stegano.lsb error: {repr(e)}"
        except Exception:
            # stegano not installed - ignore and proceed
            pass

        # 2) Manual fallback (always attempt)
        manual = self.manual_lsb_extract(image_path, lsb_bits=1, channels=(0,1,2), max_bytes=200000)
        if isinstance(manual, dict) and 'error' in manual:
            if res.get('error'):
                res['error'] += f" | manual_error: {manual['error']}"
            else:
                res['error'] = f"manual_error: {manual['error']}"
            return res

        score = manual.get('printable_ratio', 0.0)
        sample = manual.get('sample_text', '') or ''
        b64 = manual.get('bytes_b64')

        # friendlier heuristics:
        #  - any of the keywords OR
        #  - printable ratio >= 0.15 (looser) OR
        #  - sample contains >=6 alphabetic chars (covers short messages)
        keywords = ('secret','flag','password','this','begin','http','{')
        has_keyword = any(k in sample.lower() for k in keywords)
        alpha_count = sum(1 for ch in sample if ch.isalpha())

        if has_keyword or score >= 0.15 or alpha_count >= 6:
            res.update({
                'found': True,
                'method': 'manual_lsb_1bit_rgb',
                'data_preview': sample[:512],
                'score': score,
                'data_b64': b64
            })
        else:
            res.update({
                'found': False,
                'method': 'manual_lsb_1bit_rgb',
                'data_preview': sample[:512],
                'score': score,
                'data_b64': b64
            })

        return res


    def binwalk_analysis(self, image_path):
        """Embedded data detection using binwalk CLI"""
        if not self.binwalk_available:
            return {'found': False, 'error': 'Binwalk not available'}
        
        try:
            if not os.path.exists(image_path):
                return {'found': False, 'error': 'File not found'}
            
            result = subprocess.run(['binwalk', image_path], 
                                  capture_output=True, text=True)
            
            # Check for common embedded file signatures
            embedded_indicators = ['zip', 'rar', 'png', 'jpg', 'gif', 'pdf', 'executable']
            found_embedded = any(indicator in result.stdout.lower() for indicator in embedded_indicators)
            
            return {
                'found': found_embedded,
                'output': result.stdout
            }
        except Exception as e:
            return {'found': False, 'error': f'Binwalk error: {str(e)}'}
    
    def stegdetect_cli(self, image_path):
        """StegDetect CLI tool"""
        if not self.stegdetect_available:
            return {'found': False, 'error': 'StegDetect not installed'}
        
        try:
            if not os.path.exists(image_path):
                return {'found': False, 'error': 'File not found'}
            
            result = subprocess.run(['stegdetect', image_path], 
                                  capture_output=True, text=True)
            
            # More robust detection of stegdetect results
            output_lower = result.stdout.lower()
            found = any(x in output_lower for x in ['positive', 'steganography', 'jsteg', 'jphide'])
            
            return {
                'found': found,
                'output': result.stdout
            }
        except Exception as e:
            return {'found': False, 'error': f'StegDetect error: {str(e)}'}
    
    def stegonline_check(self, image_path):
        """StegOnline web service (conceptual)"""
        return {'found': False, 'info': 'Manual check required at https://stegonline.georgeom.net/'}
    
    def exiftool_check(self, image_path):
        """Check for metadata anomalies using exiftool"""
        try:
            result = subprocess.run(['exiftool', image_path], 
                                  capture_output=True, text=True)
            
            # Look for suspicious metadata
            metadata = result.stdout
            suspicious_metadata = [
                line for line in metadata.split('\n') 
                if any(keyword in line.lower() for keyword in ['comment', 'software', 'copyright', 'warning', 'note'])
            ]
            
            return {
                'found': bool(metadata.strip()),
                'has_suspicious': len(suspicious_metadata) > 0,
                'suspicious_metadata': suspicious_metadata,
                'metadata': metadata
            }
        except Exception as e:
            return {'found': False, 'error': f'ExifTool error: {str(e)}'}
    
    def strings_analysis(self, image_path):
        """Extract strings from image file"""
        try:
            result = subprocess.run(['strings', image_path], 
                                  capture_output=True, text=True)
            
            strings_list = result.stdout.split('\n')
            suspicious_keywords = ['pass', 'key', 'secret', 'flag', 'hidden', 'stego', 'password', 'encrypt']
            suspicious_strings = [
                s for s in strings_list 
                if len(s) > 8 and any(keyword in s.lower() for keyword in suspicious_keywords)
            ]
            
            return {
                'found': len(suspicious_strings) > 0,
                'suspicious_strings': suspicious_strings,
                'total_strings': len(strings_list)
            }
        except Exception as e:
            return {'found': False, 'error': f'Strings error: {str(e)}'}
    
    def file_command_check(self, image_path):
        """Use file command to detect file type anomalies"""
        try:
            result = subprocess.run(['file', image_path], 
                                  capture_output=True, text=True)
            return {
                'file_info': result.stdout.strip(),
                'is_image': 'image' in result.stdout.lower()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def comprehensive_check(self, image_path):
        """All steganography detection methods (return structures, no file writes)."""
        if not os.path.exists(image_path):
            return {'error': f'File {image_path} not found'}

        return {
            'lsb_steganography': self.stegano_lsb(image_path),              # dict
            'appended_signatures': self.find_appended_signatures(image_path),  # list
            'embedded_data': self.binwalk_analysis(image_path),
            'stegdetect': self.stegdetect_cli(image_path),
            'stegonline': self.stegonline_check(image_path),
            'metadata': self.exiftool_check(image_path),
            'strings': self.strings_analysis(image_path),
            'file_info': self.file_command_check(image_path)
        }


# Usage
if __name__ == "__main__":
   # detector = SteganographyDetector()
    
    d = SteganographyDetector()
    r = d.stegano_lsb("/home/viru/working/canvas.png")
    import json
    print(json.dumps(r, indent=2)[:2000])

    
    # # Test with a file
    # test_file = "/home/viru/working/canvas.png"
    # if os.path.exists(test_file):
    #     result = detector.comprehensive_check(test_file)
    #     print("Steganography Detection Results:")
    #     print("=" * 50)
        
    #     for method, data in result.items():
    #         print(f"\n{method.upper().replace('_', ' ')}:")
    #         print("-" * 30)

    #         # errors
    #         if isinstance(data, dict) and 'error' in data:
    #             print(f"  Error: {data['error']}")
    #             continue

    #         # file_info is special
    #         if method == 'file_info' and isinstance(data, dict):
    #             print(f"  Info: {data.get('file_info', 'N/A')}")
    #             print(f"  Is Image: {data.get('is_image', 'N/A')}")
    #             continue

    #         # LSB stego result (dict)
    #         if method == 'lsb_steganography' and isinstance(data, dict):
    #             print(f"  Found: {data.get('found', 'N/A')}")
    #             print(f"  Method: {data.get('method', 'N/A')}")
    #             if data.get('data_preview'):
    #                 print(f"  Preview: {data.get('data_preview')}")
    #             if data.get('error'):
    #                 print(f"  Error: {data.get('error')}")
    #             continue

    #         # appended_signatures is a list
    #         if method in ('appended_signatures', 'embedded_data') and isinstance(data, list):
    #             if not data:
    #                 print("  Found: False")
    #             else:
    #                 print(f"  Found: True (entries: {len(data)})")
    #                 # print condensed info
    #                 for entry in data:
    #                     if isinstance(entry, dict):
    #                         print(f"   - marker: {entry.get('marker')} appended_len: {entry.get('appended_len')}")
    #                         for sig in entry.get('embedded_signatures', []):
    #                             print(f"     -> {sig.get('type')} at abs_offset {sig.get('abs_offset')} len {sig.get('length')}")
    #             continue

    #         # fallback printing for other structures
    #         if isinstance(data, dict):
    #             print(f"  Found: {data.get('found', 'N/A')}")
    #             if data.get('output'):
    #                 out = data.get('output')
    #                 print(f"  Output (snippet): {out[:200]}")
    #             if data.get('suspicious_strings'):
    #                 print(f"  Suspicious strings: {data.get('suspicious_strings')}")
    #         else:
    #             # unknown type
    #             print("  Result:", repr(data)[:200])


    # else:
    #     print(f"Test file {test_file} not found. Please provide a valid image file.")
    #     print("Available test files:")
    #     # List potential test files in current directory
    #     for file in os.listdir('.'):
    #         if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
    #             print(f"  - {file}")