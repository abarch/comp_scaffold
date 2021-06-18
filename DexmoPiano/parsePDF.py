# Parse a pdf file

def parsepdf(filename):
    with open(filename, "r", errors='ignore') as f:
        line = f.readline()
        xmids = []
        startColumns = []
        while line:
            if line.startswith("/Rect"):
                # find the numbers between the [ ]
                numbersString = line[line.find("[")+1:line.find("]")]
                numbers = [float(i) for i in numbersString.split(' ')]
                xstart = numbers[0]
                xend = numbers[2]
                ystart = numbers[1]
                yend = numbers[3]
                xmid = (xstart + xend)/2
                xmids.append(xmid)
                #print(str(xmid))
            if line.startswith("/A<</URI"):
                numsString = line[line.find('.ly:')+4:line.find(')')]
                nums = [int(i) for i in numsString.split(':')]
                startColumn = nums[1]
                #print(str(startColumn))
                startColumns.append(startColumn)
            line = f.readline()

        combined = list(zip(startColumns,xmids))
        return sorted(combined)

if __name__ == "__main__":
    parsepdf('song1.pdf')
