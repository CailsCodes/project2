import board
import digitalio
import time


DS1302_REG_SECOND = (0x80)
DS1302_REG_MINUTE = (0x82)
DS1302_REG_HOUR   = (0x84)
DS1302_REG_DAY    = (0x86)
DS1302_REG_MONTH  = (0x88)
DS1302_REG_WEEKDAY= (0x8A)
DS1302_REG_YEAR   = (0x8C)
DS1302_REG_WP     = (0x8E)
DS1302_REG_CTRL   = (0x90)
DS1302_REG_RAM    = (0xC0)

RTC_SCLK = 2
RTC_CS = 5
RTC_MOSI = 3
RTC_MISO = 4
RTC_DIO = 4


class DS1302:

    def __init__(self, clk=board.GP2, dio=board.GP4, cs=board.GP5):

        self.clk = digitalio.DigitalInOut(clk)
        self.dio = digitalio.DigitalInOut(dio)
        self.cs  = digitalio.DigitalInOut(cs)

        self.clk.direction = digitalio.Direction.OUTPUT
        self.cs.direction = digitalio.Direction.OUTPUT
        self.dio.direction = digitalio.Direction.OUTPUT

        self.cs.value = False
        self.clk.value = False

        
    def DecToHex(self, dat):
        return (dat//10) * 16 + (dat%10)


    def HexToDec(self, dat):
        return (dat//16) * 10 + (dat%16)


    def write_byte(self, dat):
        self.dio.direction = digitalio.Direction.OUTPUT
        for i in range(8):
            self.dio.value = ((dat >> i) & 1)
            self.clk.value = True
            self.clk.value = False


    def read_byte(self):
        d = 0
        self.dio.direction = digitalio.Direction.INPUT
        for i in range(8):
            d = d | (self.dio.value<<i)
            self.clk.value = True
            self.clk.value = False
        return d


    def getReg(self, reg):
        self.cs.value = True
        self.write_byte(reg)
        t = self.read_byte()
        self.cs.value = False
        return t


    def setReg(self, reg, dat):
        self.cs.value = True
        self.write_byte(reg)
        self.write_byte(dat)
        self.cs.value = False


    def wr(self, reg, dat):
        self.setReg(DS1302_REG_WP, 0)
        self.setReg(reg, dat)
        self.setReg(DS1302_REG_WP, 0x80)


    def start(self):
        t = self.getReg(DS1302_REG_SECOND + 1)
        self.wr(DS1302_REG_SECOND, t & 0x7f)


    def stop(self):
        t = self.getReg(DS1302_REG_SECOND + 1)
        self.wr(DS1302_REG_SECOND, t | 0x80)
        

    def Second(self, second=None):
        if second:
            self.wr(DS1302_REG_SECOND, self.DecToHex(second%60))
        else:
            return self.HexToDec(self.getReg(DS1302_REG_SECOND+1))%60
            

    def Minute(self, minute=None):
        if minute:
            self.wr(DS1302_REG_MINUTE, self.DecToHex(minute%60))
        else:
            return self.HexToDec(self.getReg(DS1302_REG_MINUTE+1))
        

    def Hour(self, hour=None):
        if not hour:
            return self.HexToDec(self.getReg(DS1302_REG_HOUR+1))
        else:
            self.wr(DS1302_REG_HOUR, self.DecToHex(hour%24))


    def Weekday(self, weekday=None):
        if not weekday:
            return self.HexToDec(self.getReg(DS1302_REG_WEEKDAY+1))
        else:
            self.wr(DS1302_REG_WEEKDAY, self.DecToHex(weekday%8))


    def Day(self, day=None):
        if not day:
            return self.HexToDec(self.getReg(DS1302_REG_DAY+1))
        else:
            self.wr(DS1302_REG_DAY, self.DecToHex(day%32))


    def Month(self, month=None):
        if not month:
            return self.HexToDec(self.getReg(DS1302_REG_MONTH+1))
        else:
            self.wr(DS1302_REG_MONTH, self.DecToHex(month%13))


    def Year(self, year=None):
        if not year:
            return self.HexToDec(self.getReg(DS1302_REG_YEAR+1)) + 2000
        else:
            self.wr(DS1302_REG_YEAR, self.DecToHex(year%100))


    def DateTime(self, dat=None):
        if not dat:
            return [self.Year(), self.Month(), self.Day(), self.Weekday(), self.Hour(), self.Minute(), self.Second()]
        else:
            self.Year(dat[0])
            self.Month(dat[1])
            self.Day(dat[2])
            self.Weekday(dat[3])
            self.Hour(dat[4])
            self.Minute(dat[5])
            self.Second(dat[6])


    def ram(self, reg, dat = None):
        if dat == None:
            return self.getReg(DS1302_REG_RAM + 1 + (reg%31)*2)
        else:
            self.wr(DS1302_REG_RAM + (reg%31)*2, dat)




if __name__ == "__main__":
    ds = DS1302()

    ds.DateTime()

    ds.Year(2022)
    ds.Month(3)
    ds.Day(25)
    ds.Weekday(5)
    ds.Hour(18)
    ds.Minute(3)
    ds.Second(45)

    while True:
        print(ds.Year(),ds.Month(),ds.Day(),ds.Weekday(),ds.Hour(),ds.Minute(),ds.Second()) 
        time.sleep(5)
        
    
   
    