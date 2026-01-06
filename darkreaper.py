import sys
import asyncio
import traceback
import os
import argparse
import re
import json
from colorama import Fore, Style, init
from typing import Optional
from dr_modules.main_email import EmailResearchHandler
from dr_modules.main_username import UsernameResearchHandler
from dr_modules.main_image import ImageResearchHandler
from dr_modules.main_ip import IPResearchHandler
from dr_modules.main_phone import PhoneResearchHandler
from dr_modules.logo import interface



class AIGT:
    def __init__(self):
        self.phone_handler = PhoneResearchHandler()
        self.email_handler = EmailResearchHandler()
        self.username_handler = UsernameResearchHandler()
        self.ip_handler = IPResearchHandler()
        self.image_handler = ImageResearchHandler()
        
        # Setup command processor
        self.command_processor = CommandProcessor(self)


    def _detect_type(self, identifier):
        """Helper to detect identifier type - keep this for routing"""
        if re.match(r'^\+?[\d\s\-\(\)]{8,}\d$', identifier):
            return "phone"
        elif re.match(r'[\w\.-]+@[\w\.-]+', identifier):
            return "email"
        elif self.validator.is_valid_ip(identifier):  # Add IP validation
            return "ip"
        elif os.path.exists(identifier) or identifier.startswith(('http://', 'https://')):
            return "image"
        elif '/' in identifier :  # username-platform format
            return "username"
        return "unknown"
    
    
class CommandProcessor:
    def __init__(self, aigt):  
        self.aigt = aigt
        self.loop = asyncio.new_event_loop()
        self.parser = self.setup_parser()

    def setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description='CLI Tool with multiple commands', add_help=False)
        subparsers = parser.add_subparsers(dest='command', required=False)

        # Phone command (output is optional)
        phone_parser = subparsers.add_parser('p', help='Phone number command')
        phone_parser.add_argument('number', help='Phone number to process')
        phone_parser.add_argument('o', nargs='?', help='Output path (optional)')  # Make output optional

        # IP command (output is optional)
        ip_parser = subparsers.add_parser('i', help='IP address command')
        ip_parser.add_argument('ip', help='IP address to process')
        ip_parser.add_argument('o', nargs='?', help='Output path (optional)')

        # Username command (output is optional)
        user_parser = subparsers.add_parser('u', help='Username/platform command')
        user_parser.add_argument('username', help='Username and platform (format: username/platform)')
        user_parser.add_argument('o', nargs='?', help='Output path (optional)')

        # Email command (output is optional)
        email_parser = subparsers.add_parser('e', help='Email command')
        email_parser.add_argument('email', help='Email address to process')
        email_parser.add_argument('o', nargs='?', help='Output path (optional)')

        # Image command (output is optional)
        img_parser = subparsers.add_parser('img', help='Image investigation')
        img_parser.add_argument('path', help='Path to image file')
        img_parser.add_argument('o', nargs='?', help='Output path (optional)')

        help_parser = subparsers.add_parser('help', help='Show help')

        return parser

    def process_command(self, cmd: str):
        try:
            # Parse the command and handle SystemExit exception
            try:
                args = self.parser.parse_args(cmd.split())
            except SystemExit:
                return "Invalid command"
            
            if args.command == 'p':
                if args.o:  # With output path - save to files
                    result = self.loop.run_until_complete(
                        self.aigt.phone_handler.conduct_research_with_output(
                            args.number, 
                            args.o,
                            2
                        )
                    )
                    return json.dumps(result, indent=2)
                else:  # No output path - just show on terminal
                    research_data = self.loop.run_until_complete(
                        self.aigt.phone_handler.conduct_research(args.number, 2)
                    )
                    return json.dumps(research_data, indent=2)
            
            elif args.command == 'e':
                if args.o:  # With output path
                    result = self.loop.run_until_complete(
                        self.aigt.email_handler.conduct_research_with_output(
                            args.email,
                            args.o,
                            2
                        )
                    )
                    return json.dumps(result, indent=2)
                else:  # No output path
                    research_data = self.loop.run_until_complete(
                        self.aigt.email_handler.conduct_research(args.email, 2)
                    )
                    return json.dumps(research_data, indent=2)
            
            elif args.command == 'i':
                if args.o:  # With output path
                    result = self.aigt.ip_handler.conduct_research_with_output(
                        args.ip,
                        args.o,
                        # use_tor=False  
                    )
                    return json.dumps(result, indent=2)
                else:  # No output path
                    research_data = self.loop.run_until_complete(
                        self.aigt.ip_handler.conduct_comprehensive_research(args.ip)
                    )
                    return json.dumps(research_data, indent=2)
            
            elif args.command == 'u':
                if args.o:  # With output path
                    result = self.loop.run_until_complete(
                        self.aigt.username_handler.conduct_research_with_output(
                            args.username,
                            args.o,
                            2
                        )
                    )
                    return json.dumps(result, indent=2)
                else:  # No output path
                    research_data = self.loop.run_until_complete(
                        self.aigt.username_handler.conduct_research(args.username, 2)
                    )
                    return json.dumps(research_data, indent=2)
            
            elif args.command == 'img':
                if args.o:  # With output path
                    result = self.loop.run_until_complete(
                        self.aigt.image_handler.conduct_research_with_output(
                            args.path,
                            args.o,
                            2
                        )
                    )
                    return json.dumps(result, indent=2)
                else:  # No output path
                    research_data = self.loop.run_until_complete(
                        self.aigt.image_handler.conduct_research(args.path, 2)
                    )
                    return json.dumps(research_data, indent=2)
            
            elif args.command == 'help':
                return self.show_help()
                
            else:
                return "Invalid command"
                
        except Exception as e:
            return f"Error: {str(e)}\n{traceback.format_exc()}"
        

    def show_help(self, command=None):
        """Display help information - general or command-specific"""
        if command:
            # Command-specific help
            if command == 'p':
                help_text = """
                Phone Research Command:
                p <phone_number> [ <output_path>]
                
                Examples:
                p +14155552671                       - Research phone, show on terminal
                p +14155552671  phone_report        - Research phone, save to files
                
                This command researches phone numbers using various OSINT techniques.
                """
            elif command == 'e':
                help_text = """
                Email Research Command:
                e <email> [ <output_path>]
                
                Examples:
                e test@example.com                    - Research email, show on terminal  
                e test@example.com  email_report     - Research email, save to file
                
                This command researches email addresses using various OSINT techniques.
                """
            elif command == 'i':
                help_text = """
                IP Research Command:
                i <ip_address> [ <output_path>]
                
                Examples:
                i 8.8.8.8                            - Research IP, show on terminal
                i 8.8.8.8  ip_report                - Research IP, save to file
                
                This command researches IP addresses using various OSINT techniques.
                """
            elif command == 'u':
                help_text = """
                Username Research Command:
                u <username/platform> [ <output_path>]
                
                Format: username/platform (e.g., john/instagram)
                
                Examples:
                u john/instagram                      - Research username, show on terminal
                u john/instagram  user_report        - Research username, save to file
                
                This command researches usernames across various platforms.
                """
            elif command == 'img':
                help_text = """
                Image Research Command:
                img <image_path> [ <output_path>]
                
                Examples:
                img photo.jpg                         - Research image, show on terminal
                img photo.jpg  image_report          - Research image, save to file
                
                This command performs reverse image search and EXIF data analysis.
                """
            else:
                help_text = f"Unknown command: {command}. Type 'help' for general help."
        else:
            # General help
            help_text = """
            AIGT - Automated Intelligence Gathering Tool
            
            Command Syntax:
            p <phone_number> [ <output_path>]    - Phone research (optional save)
            e <email> [ <output_path>]           - Email research (optional save)  
            i <ip_address> [ <output_path>]      - IP research (optional save)
            u <username/platform> [ <output_path>] - Username research (optional save)
            img <image_path> [ <output_path>]    - Image research (optional save)
            
            For detailed help on a specific command, type: help <command>
            Examples: help p, help e, help img, etc.
            
            General Examples:
            p +14155552671                       - Research phone, show on terminal
            e test@example.com                    - Research email, show on terminal  
            i 8.8.8.8                            - Research IP, show on terminal
            u john/instagram                      - Research username, show on terminal
            img photo.jpg                         - Research image, show on terminal
            """
        
        return help_text

    def validate_json_path(self, path: str) -> bool:
        """Validate the output path ends with .json and is writable"""
        if not path.lower().endswith('.json'):
            return False
        
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                return False
        
        try:
            with open(path, 'w') as test_file:
                json.dump({"test": "validation"}, test_file)
            os.remove(path)
            return True
        except (IOError, OSError):
            return False

    def process_output(self, args: argparse.Namespace) -> str:
        """Simple output method - just validates path, actual saving happens elsewhere"""
        try:
            if not self.validate_json_path(args.path):
                return "Error: Output path must be a valid .json file path"
            
            return f"Output path validated: {args.path}. Use a research command first to generate data."
            
        except Exception as e:
            return f"Error: {str(e)}"



def main():
    aigt = AIGT()  
    processor = CommandProcessor(aigt) 
    interface()
    processor.show_help()

    try:
        while True:
            try:
                cmd = input(f"{Fore.BLUE}Dark☠️Reaper ִֶָ. ..𓂃 ࣪ ִֶָ🪽{Style.RESET_ALL} ").strip()
                if cmd.lower() in ['exit', 'quit']:
                    break
                result = processor.process_command(cmd)
                print(result)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")
    finally:
        # Clean up the event loop
        processor.loop.close()

if __name__ == "__main__":
    main()