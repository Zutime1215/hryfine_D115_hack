import pexpect
from time import sleep
from random import randrange

time_header = "df0009"
vibrate_packet = "df00060402100b000101"
common = "0210010004"
handle = "0x002b"

def date_encode(date):
    dt = ''
    dt += '{0:06b}'.format(date[0])
    dt += '{0:04b}'.format(date[1])
    dt += '{0:05b}'.format(date[2])
    dt += '{0:05b}'.format(date[3])
    dt += '{0:06b}'.format(date[4])
    dt += '{0:06b}'.format(date[5])

    return str(hex(int(dt, 2)))[2:]

def date_decode(dt):
    dt_bin = '{0:032b}'.format(int(dt, 16))
    return (
        int(dt_bin[0:6], 2),
        int(dt_bin[6:10], 2),
        int(dt_bin[10:15], 2),
        int(dt_bin[15:20], 2),
        int(dt_bin[20:26], 2),
        int(dt_bin[26:], 2),
    )

def checksumCalc(dt_enc):
    cmd = time_header + common + dt_enc

    sum = 0
    for i in range(0, len(cmd) - 1, 2):
        h = cmd[i : i + 2]
        d = int(h, 16)
        sum += d

    sum = sum % 256
    return str(hex(sum))[2:]

def gen_date_msg(date):
    date_enc = date_encode(date)
    chk_sum = checksumCalc(date_enc)
    return time_header + chk_sum + common + date_enc


def main(mac):
    try:
        gatttool = pexpect.spawn(f"gatttool -b {mac} -I")
        
        gatttool.sendline("connect")
        gatttool.expect("Connection successful", timeout=10)
        print("Connected to the device!")

        while True:
            print("1. Random Date Time.\n2. Change Time.\n3. Enable Vibrate.\n99. Exit.")
            option = input('>> ')
            if option == '99':
                gatttool.sendline("disconnect")
                gatttool.close()
                print("Connection closed!")
                break
            elif option == "1":
                for i in range(30):
                    date = (25, randrange(12), randrange(30), randrange(23), randrange(60), 44)
                    command = f"char-write-req {handle} {gen_date_msg(date)}"
                    gatttool.sendline(command)
                    gatttool.expect("Characteristic value was written successfully", timeout=5)
                    print(f"Sent: {date}")
                    sleep(.7)

            elif option == "2":
                print("Give a date-time like this. 25 1 8 21 30 \n(These are year month day hour minute)")
                strDate = input('>> ')
                tupleDate = tuple(map(int, strDate.split()))
                tupleDate += (0,)
                command = f"char-write-req {handle} {gen_date_msg(tupleDate)}"
                print(tupleDate, command)
                gatttool.sendline(command)
                gatttool.expect("Characteristic value was written successfully", timeout=5)

            elif option == '3':
                command = f"char-write-req {handle} {vibrate_packet}"
                gatttool.sendline(command)
        
    except pexpect.exceptions.TIMEOUT:
        print("Connection timed out or an error occurred. Trying again.")
        sleep(3)
        main()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    mac = input("Enter Mac Address: ")
    main(mac)