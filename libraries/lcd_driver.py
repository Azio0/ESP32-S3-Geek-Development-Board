#/-----------------------------------------
#/ A substitute driver instead of st7789
#/ Feel free to use, change or redistribute
#/-----------------------------------------
from machine import Pin, SPI, PWM
import framebuf

BL = 7
DC = 8
CS = 10
SCK = 12
MOSI = 11
RST = 9

class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.cs(1)
        self.spi = SPI(1, 50_000_000, polarity=0, phase=0,
                       sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

    def write_cmd(self, cmd):
        self.cs(1); self.dc(0); self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1); self.dc(1); self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        self.rst(1); self.rst(0); self.rst(1)
        self.write_cmd(0x36); self.write_data(0x70)
        self.write_cmd(0x3A); self.write_data(0x05)
        self.write_cmd(0xB2)
        for d in [0x0C,0x0C,0x00,0x33,0x33]: self.write_data(d)
        self.write_cmd(0xB7); self.write_data(0x35)
        self.write_cmd(0xBB); self.write_data(0x19)
        self.write_cmd(0xC0); self.write_data(0x2C)
        self.write_cmd(0xC2); self.write_data(0x01)
        self.write_cmd(0xC3); self.write_data(0x12)
        self.write_cmd(0xC4); self.write_data(0x20)
        self.write_cmd(0xC6); self.write_data(0x0F)
        self.write_cmd(0xD0); self.write_data(0xA4); self.write_data(0xA1)
        self.write_cmd(0xE0)
        for d in [0xD0,0x04,0x0D,0x11,0x13,0x2B,0x3F,0x54,0x4C,0x18,0x0D,0x0B,0x1F,0x23]: self.write_data(d)
        self.write_cmd(0xE1)
        for d in [0xD0,0x04,0x0C,0x11,0x13,0x2C,0x3F,0x44,0x51,0x2F,0x1F,0x1F,0x20,0x23]: self.write_data(d)
        self.write_cmd(0x21)
        self.write_cmd(0x11)
        self.write_cmd(0x29)

    @micropython.viper
    def swap(self):
        buf=ptr8(self.buffer)
        for x in range(0,240*135*2,2):
            t=buf[x]; buf[x]=buf[x+1]; buf[x+1]=t

    def show(self):
        self.write_cmd(0x2A)
        for d in [0x00,0x28,0x01,0x17]: self.write_data(d)
        self.write_cmd(0x2B)
        for d in [0x00,0x35,0x00,0xBB]: self.write_data(d)
        self.write_cmd(0x2C)
        self.cs(1); self.dc(1); self.cs(0)
        self.swap(); self.spi.write(self.buffer); self.swap()
        self.cs(1)

pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(65535)
lcd = LCD_1inch14()

def show_text(text, x=10, y=60, color=0xFFFF, clear=True, scale=1):
    if clear:
        lcd.fill(0x0000)
    if scale == 1:
        lcd.text(text, x, y, color)
    else:
        for i, ch in enumerate(text):
            fb = framebuf.FrameBuffer(bytearray(8*8), 8, 8, framebuf.MONO_HLSB)
            fb.text(ch, 0, 0, 1)
            for cx in range(8):
                for cy in range(8):
                    if fb.pixel(cx, cy):
                        for dx in range(scale):
                            for dy in range(scale):
                                lcd.pixel(x + i*8*scale + cx*scale + dx, y + cy*scale + dy, color)
    lcd.show()

def clear(color=0x0000):
    lcd.fill(color)
    lcd.show()
