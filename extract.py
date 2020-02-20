import struct

CHUNK = 1024 * 1024 * 100 #process 100 megs at a time.

TOPLEVEL = ['ftyp', 'wide', 'mdat', 'moov']

def look(data):
    for tl in TOPLEVEL:
        if tl in data:
            print "LOOK:",tl
            yield tl
def extract(f,tag,position):
    loc = f.tell()
    f.seek(position)
    dat = f.read(4)
    assert tag == f.read(4)
    get_Tag_seek2next(f,position)
    f.seek(loc)

def get_Tag_seek2next(f, start=0):
    f.seek(start, 0)
    while 1:
        current_start = f.tell()
        dat = f.read(8)
        already_seeked = 8
        extended = False
        if dat:
            size = struct.unpack(">I",dat[:4])[0]
            tag = dat[4:]
            if size == 1:
                extended = True
                dat = f.read(8)
                if dat:
                    already_seeked += 8
                    size = struct.unpack(">Q",dat)[0]
                else:
                    break
            elif size == 0:
                break
            print "    EXTRACT:",tag+"@%d-%r-%d-%d"%(current_start,extended,size,current_start+size)


            f.seek(size-already_seeked,1)
        else:
            break

def process_data(in_disk, out_disk, start, end):
    if end == -1:
        in_disk.seek(0, 2)
        end = in_disk.tell()


    in_disk.seek(start, 0)
    while 1:
        position = in_disk.tell()
        if position >= end:
            break
        if position + CHUNK <= end:
            buffer = in_disk.read(CHUNK)
        else:
            buffer = in_disk.read(end - position)
        if len(buffer) == 0:
            break
        out_disk.write(buffer)

if __name__=='__main__':
    import sys
    if len(sys.argv) == 5:
        in_disk = open(sys.argv[1],'rb')
        out_disk = open(sys.argv[2],'ab')
        start = int(sys.argv[3])
        end = int(sys.argv[4])
        process_data(in_disk, out_disk, start, end)
    else:
        print "Usage: python extract.py /path/to/disk.dat /path/to/out.dat start end"

