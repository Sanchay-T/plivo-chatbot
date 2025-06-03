#!/usr/bin/env python3
"""
Helper script to update streams.xml with the correct server URL from environment variables
"""

import os
from dotenv import load_dotenv

def update_streams_xml():
    """Update streams.xml with the SERVER_URL from .env"""
    load_dotenv()
    
    server_url = os.getenv("SERVER_URL")
    if not server_url:
        print("❌ ERROR: SERVER_URL not found in .env file")
        print("Please set SERVER_URL=your-ngrok-url.ngrok.io in your .env file")
        return False
    
    # Read the template
    template_path = "templates/streams.xml.template"
    output_path = "templates/streams.xml"
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Replace placeholder with actual URL
        updated_content = content.replace('<your server url>', server_url)
        
        # Write the updated file
        with open(output_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Successfully updated {output_path}")
        print(f"   WebSocket URL: wss://{server_url}/ws")
        return True
        
    except FileNotFoundError:
        print(f"❌ ERROR: {template_path} not found")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Updating streams.xml with server URL...")
    success = update_streams_xml()
    
    if success:
        print("\n🎉 Configuration complete!")
        print("You can now run: python server.py")
    else:
        print("\n💡 Please fix the issues above and try again.") 