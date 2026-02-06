"""
Interactive Backlight Validation for URSA MINOR 32

Tests each of the 4 backlight zones individually.
User confirms which zone lights up.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import hid
except ImportError:
    print("Error: hidapi not installed")
    print("Install with: pip install hidapi")
    sys.exit(1)

VID = 0x4098
PID = 0xB920

# Backlight zones to test
BACKLIGHT_ZONES = [
    {
        'name': '1. Throttle Backlight (potencias)',
        'description': 'Iluminación de las palancas de throttle',
        'cmd_type': 0x10,
        'control_id': 0x00
    },
    {
        'name': '2. Marker Backlight (ENG FIRE/FAULT LEDs)',
        'description': 'Iluminación de fondo de los LEDs ENG',
        'cmd_type': 0x10,
        'control_id': 0x02
    },
    {
        'name': '3. Backlight 2 (Módulo 32-pack)',
        'description': 'Iluminación del módulo 32-pack (Flaps/Spoiler)',
        'cmd_type': 0x01,
        'control_id': 0x00
    },
    {
        'name': '4. Digital Tube Backlight (LCD)',
        'description': 'Iluminación del display LCD',
        'cmd_type': 0x01,
        'control_id': 0x02
    }
]


def send_backlight_command(device, cmd_type, control_id, intensity):
    """
    Send backlight control command.
    
    Args:
        device: HID device handle
        cmd_type (int): Command type
        control_id (int): Control identifier
        intensity (int): Brightness 0-255
    """
    buffer = [0] * 64
    buffer[0] = 0x02
    buffer[1] = cmd_type
    buffer[2] = 0xb9
    buffer[3] = 0x00
    buffer[4] = 0x00
    buffer[5] = 0x03
    buffer[6] = 0x49
    buffer[7] = control_id
    buffer[8] = intensity
    
    try:
        device.write(buffer)
    except Exception as e:
        print(f"Error: {e}")


def test_backlight(device, zone):
    """
    Test a single backlight zone.
    
    Args:
        device: HID device handle
        zone (dict): Backlight zone configuration
    """
    print("\n" + "=" * 70)
    print(f"Testing: {zone['name']}")
    print("=" * 70)
    print(f"Description: {zone['description']}")
    print(f"Command: cmd_type=0x{zone['cmd_type']:02X}, control_id=0x{zone['control_id']:02X}")
    print()
    
    input("Press Enter to test this backlight...")
    print()
    
    # Fade in
    print("Fading IN...")
    for brightness in [0, 64, 128, 192, 255]:
        send_backlight_command(device, zone['cmd_type'], zone['control_id'], brightness)
        time.sleep(0.3)
    
    time.sleep(1.0)
    
    # Fade out
    print("Fading OUT...")
    for brightness in [192, 128, 64, 0]:
        send_backlight_command(device, zone['cmd_type'], zone['control_id'], brightness)
        time.sleep(0.3)
    
    print()
    print("Did you see the correct backlight zone light up?")
    print(f"Expected: {zone['description']}")
    print()
    print("  y. Yes - Correct")
    print("  n. No - Wrong zone or no light")
    print("  s. Skip")
    print()
    
    response = input("Your answer: ").strip().lower()
    
    if response == 'y':
        print(f"✓ VERIFIED: {zone['name']}")
        return True
    elif response == 'n':
        print(f"✗ FAILED: {zone['name']} - Did not match expected zone")
        return False
    else:
        print(f"⊘ SKIPPED: {zone['name']}")
        return None


def main():
    """Main validation workflow"""
    
    print("=" * 70)
    print("URSA MINOR 32 - Backlight Validation")
    print("=" * 70)
    print()
    print("This script tests each backlight zone individually.")
    print("You will see each zone fade IN and OUT.")
    print()
    print("4 zones to validate:")
    for zone in BACKLIGHT_ZONES:
        print(f"  • {zone['name']}")
    print()
    
    # Open device
    print("Opening device...")
    try:
        device = hid.device()
        device.open(VID, PID)
        print("✓ Device opened")
        print()
    except Exception as e:
        print(f"✗ Device not found: {e}")
        return 1
    
    try:
        # Test each zone
        results = {}
        
        for zone in BACKLIGHT_ZONES:
            result = test_backlight(device, zone)
            results[zone['name']] = result
        
        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print()
        
        verified = sum(1 for r in results.values() if r is True)
        failed = sum(1 for r in results.values() if r is False)
        skipped = sum(1 for r in results.values() if r is None)
        
        print(f"Verified: {verified}/4")
        print(f"Failed:   {failed}/4")
        print(f"Skipped:  {skipped}/4")
        print()
        
        print("Detailed results:")
        for name, result in results.items():
            if result is True:
                status = "✓ VERIFIED"
            elif result is False:
                status = "✗ FAILED"
            else:
                status = "⊘ SKIPPED"
            print(f"  {status} - {name}")
        
        print()
        
        if verified == 4:
            print("🎉 ALL BACKLIGHTS VERIFIED!")
        elif failed > 0:
            print("⚠️  Some backlights did not work as expected")
            print("   Check wiring or control mappings")
        
    finally:
        # Turn off all backlights
        for zone in BACKLIGHT_ZONES:
            send_backlight_command(device, zone['cmd_type'], zone['control_id'], 0)
        
        device.close()
        print("\nDevice closed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
