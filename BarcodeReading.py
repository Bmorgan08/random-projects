import usb.core
import usb.util

dev = usb.core.find(idVendor=0x1c6c, idProduct=0xc00c)
if dev is None:
    raise ValueError("Keyboard not found")

dev.reset()

# Interface 2 is the active keyboard interface
intf_num = 2
cfg = dev.get_active_configuration()
intf = cfg[(intf_num, 0)]


before = dev.is_kernel_driver_active(intf_num)
print("Interface 2 BEFORE:", before)
if before:
    dev.detach_kernel_driver(intf_num)
after = dev.is_kernel_driver_active(intf_num)
print("Interface 2 AFTER:", after)

usb.util.claim_interface(dev, intf_num)

# Get the IN endpoint for this interface
ep = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
)

print("Listening for keypresses on Interface 2...")

while True:
    try:
        data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize, timeout=1000)
        print(list(data))  # raw HID bytes
        if data[1] == 1 and data[3] == 6: #'^C' pressed
            print("Ctrl+C detected, exiting.")
            break
    except usb.core.USBError as e:
        if e.errno != 110:  # 110 = timeout
            raise