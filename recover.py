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

def process_data(f, start = 0):
    #hack to correctly account for file position since we always keep 8 bytes in the buffer
    buffer = "00000000" 
    #Keep tract of the file position relative to the beginning of the buffer
    POS = start-CHUNK
    # store any chucks that we find.
    found = {}
    f.seek(start, 0)
    while 1:
        buffer += f.read(CHUNK)
        if len(buffer) == 8:
            break
        POS += CHUNK
        for tag in look(buffer):
            pos = POS + buffer.index(tag) - 4 - 8
            extract(f, tag, pos)
        buffer = buffer[-8:]
    f.seek(0, 2)
    print "END: %d"%(f.tell())
    return found

if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        disk = open(sys.argv[1],'rb')
        process_data(disk)
    elif len(sys.argv) == 3:
        disk = open(sys.argv[1],'rb')
        process_data(disk, start=int(sys.argv[2]))
    else:
        print "Usage: python recover.py /path/to/disk.dat"

