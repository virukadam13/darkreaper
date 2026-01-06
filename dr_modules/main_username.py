# username_research.py
import json
import re
import os
import sys
import asyncio
from datetime import datetime
from typing import Dict
from .username.social_media_info import PlatformSpecificIntelligence
from .username.social_check import SherlockWrapper, MaigretWrapper, AsyncSocialChecker
from .username.darkweb_search import OnionSearch, DarkFailChecker, Ahmia

class UsernameResearchHandler:
    def __init__(self):
        self.platform_intel = PlatformSpecificIntelligence()
        self.sherlock = SherlockWrapper()
        self.maigret = MaigretWrapper()
        self.async_checker = AsyncSocialChecker()
        
        # Initialize darkweb search components
        self.onion_searcher = OnionSearch(api_key="sk-")
        self.darkfail_checker = DarkFailChecker()
        self.ahmia_searcher = Ahmia()

    async def conduct_research(self, username_platform: str, depth: int = 2) -> Dict:
        """
        Username research compatible with DarkReaper interface
        """
        print(f"\n🔍 Researching: {username_platform}")
        print("=" * 40)
        
        start_time = datetime.now()
        
        # DarkReaper expects this exact structure
        results = {
            "meta": {
                "input": username_platform,
                "start_time": start_time.isoformat(),
                "depth": depth
            },
            "raw": {},
            "success": True
        }

        try:
            if '/' in username_platform:
                # Focused platform research
                username, platform = username_platform.split('/', 1)
                platform = self._normalize_platform(platform)
                
                print(f"🎯 Focused on {platform}")
                
                # Platform deep dive
                print(f"\n1. Platform intelligence...")
                platform_data = await self._gather_platform_intel(username, platform)
                results["raw"]["platform_intel"] = platform_data
                
                # Check other platforms
                print(f"\n2. Checking other platforms...")
                other_data = await self._check_other_platforms(username)
                results["raw"]["other_platforms"] = other_data
                
            else:
                # Broad username research
                username = username_platform
                print(f"🌐 Broad search for {username}")
                
                # Quick Sherlock scan
                print(f"\n1. Quick scan (Sherlock)...")
                sherlock_data = await self._run_sherlock(username)
                results["raw"]["sherlock"] = sherlock_data
                
                # Deep Maigret scan
                print(f"\n2. Deep scan (Maigret)...")
                maigret_data = await self._run_maigret(username)
                results["raw"]["maigret"] = maigret_data

            # Enhanced dark web check
            print(f"\n3. Dark web investigation...")
            darkweb_data = await self._enhanced_darkweb_check(username)
            results["raw"]["darkweb"] = darkweb_data
            
            print(f"\n✅ Research completed!")
            
        except Exception as e:
            results["success"] = False
            results["error"] = f"Research failed: {str(e)}"
            print(f"❌ Error: {str(e)}")
        
        results["meta"]["end_time"] = datetime.now().isoformat()
        results["meta"]["processing_time"] = str(datetime.now() - start_time)
        return results

    async def _gather_platform_intel(self, username: str, platform: str) -> Dict:
        """Get detailed platform info"""
        try:
            result = self.platform_intel.gather_info(username, platform)
            if result.get("success"):
                data = result.get("data", {})
                print(f"   ✅ Found: {data.get('name', 'N/A')}")
                if data.get('followers'):
                    print(f"   👥 Followers: {data.get('followers')}")
            return result
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            return {"error": str(e)}

    async def _check_other_platforms(self, username: str) -> Dict:
        """Check username on other platforms"""
        try:
            results = await self.async_checker.check_all_sites(username)
            found = [url for url, exists, _ in results if exists]
            print(f"   ✅ Found on {len(found)} platforms")
            return {"found": found, "total_checked": len(results)}
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            return {"error": str(e)}

    async def _run_sherlock(self, username: str) -> Dict:
        """Run Sherlock with proper error handling"""
        # try:
        #     result = self.sherlock.check_username(username)
        #     print(f"   🔧 Sherlock raw result: {result}")
            
        #     if "Found" in result and "accounts" in result:
        #         # Extract the number of found accounts
        #         found_match = re.search(r'Found (\d+) accounts', result)
        #         if found_match:
        #             found_count = int(found_match.group(1))
        #             print(f"   ✅ Found {found_count} accounts with Sherlock")
        #             return {"found": found_count, "result": result}
            
        #     print("   ⚠️  No accounts found with Sherlock")
        #     return {"found": 0, "result": result}
            
        # except Exception as e:
        #     print(f"   ❌ Sherlock failed: {str(e)}")
        #     return {"error": str(e), "found": 0}
        sherlock = SherlockWrapper()
        sherlock_result = sherlock.check_username(username)
        return sherlock_result

    async def _run_maigret(self, username: str) -> Dict:
        """Run Maigret with proper error handling"""
        try:
            result = self.maigret.scan(username)
            print(f"   🔧 Maigret raw result: {result}")
            
            if "Found" in result and "accounts" in result:
                found_match = re.search(r'Found (\d+) accounts', result)
                if found_match:
                    found_count = int(found_match.group(1))
                    print(f"   ✅ Found {found_count} accounts with Maigret")
                    lines = result.split('\n')
                    return {"found": found_count, "result": lines}

            
            print("   ⚠️  No accounts found with Maigret")
            return {"found": 0, "result": result}
            
        except Exception as e:
            print(f"   ❌ Maigret failed: {str(e)}")
            return {"error": str(e), "found": 0}

    async def _enhanced_darkweb_check(self, username: str) -> Dict:
        """Enhanced dark web investigation using multiple sources"""
        darkweb_results = {
            "ahmia": {},
            "onion_search": {},
            "darkfail": {},
            "summary": {}
        }
        
        try:
            print("   🔍 Checking Ahmia...")
            # Ahmia search
            ahmia_results = self.ahmia_searcher.search(username)
            darkweb_results["ahmia"] = {
                "results": ahmia_results,
                "count": len(ahmia_results) if ahmia_results else 0
            }
            print(f"   ✅ Ahmia: {darkweb_results['ahmia']['count']} results")

            # OnionSearch (if API key is valid)
            print("   🔍 Checking OnionSearch...")
            try:
                onion_results = self.onion_searcher.search(username, pages=1)
                darkweb_results["onion_search"] = {
                    "results": onion_results,
                    "count": len(onion_results)
                }
                print(f"   ✅ OnionSearch: {darkweb_results['onion_search']['count']} results")
            except Exception as e:
                darkweb_results["onion_search"] = {"error": str(e)}
                print(f"   ⚠️  OnionSearch: {str(e)}")

            # DarkFail monitoring sites
            print("   🔍 Checking DarkFail...")
            try:
                darkfail_results = self.darkfail_checker.run(query=username, save_json=None)
                darkweb_results["darkfail"] = {
                    "onions_found": darkfail_results.get("count_onions", 0),
                    "onions": darkfail_results.get("onions", []),
                    "pgp_links": darkfail_results.get("pgp_links", [])
                }
                print(f"   ✅ DarkFail: {darkweb_results['darkfail']['onions_found']} onions")
            except Exception as e:
                darkweb_results["darkfail"] = {"error": str(e)}
                print(f"   ⚠️  DarkFail: {str(e)}")

            # Create summary
            total_mentions = (
                darkweb_results["ahmia"]["count"] +
                darkweb_results["onion_search"].get("count", 0) +
                darkweb_results["darkfail"].get("onions_found", 0)
            )
            
            darkweb_results["summary"] = {
                "total_mentions": total_mentions,
                "sources_checked": 3,
                "risk_level": self._assess_darkweb_risk(total_mentions)
            }
            
            print(f"   📊 Darkweb Summary: {total_mentions} total mentions")
            print(f"   🚨 Risk Level: {darkweb_results['summary']['risk_level']}")
            
        except Exception as e:
            print(f"   ❌ Dark web investigation failed: {str(e)}")
            darkweb_results["error"] = str(e)
            
        return darkweb_results

    def _assess_darkweb_risk(self, mention_count: int) -> str:
        """Assess risk level based on dark web mentions"""
        if mention_count == 0:
            return "LOW"
        elif mention_count <= 3:
            return "MEDIUM"
        elif mention_count <= 10:
            return "HIGH"
        else:
            return "CRITICAL"

    def _normalize_platform(self, platform: str) -> str:
        """Normalize platform name"""
        platform_map = {
            'instagram': 'instagram.com',
            'twitter': 'twitter.com', 
            'facebook': 'facebook.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com'
        }
        return platform_map.get(platform.lower(), platform)

    async def conduct_research_with_output(self, username_platform: str, output_path: str, depth: int = 2) -> Dict:
        """Research and save results - compatible with DarkReaper"""
        research_data = await self.conduct_research(username_platform, depth)
        
        # Save JSON report
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        print(f"\n💾 Report saved: {json_path}")
        
        # Return format expected by DarkReaper
        return {
            "success": True,
            "message": "Username research completed and saved",
            "username_platform": username_platform,
            "json_output_path": os.path.abspath(json_path),
            "findings_count": len(research_data.get("raw", {}))
        }

# Sync wrappers that DarkReaper expects
def sync_conduct_research(username_platform: str, depth: int = 2) -> Dict:
    """Sync wrapper - DarkReaper calls this"""
    handler = UsernameResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(handler.conduct_research(username_platform, depth))
    finally:
        loop.close()

def sync_conduct_research_with_output(username_platform: str, output_path: str, depth: int = 2) -> Dict:
    """Sync wrapper with output - DarkReaper calls this"""
    handler = UsernameResearchHandler()
    return asyncio.run(handler.conduct_research_with_output(username_platform, output_path, depth))

# Test if run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else "report"
        sync_conduct_research_with_output(target, output)
    else:
        print("Usage: python username_research.py <username> [output]")
        print("Examples:")
        print("  python username_research.py john_doe")
        print("  python username_research.py johndoe/instagram instagram_report")