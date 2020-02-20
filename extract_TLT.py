""" Extract Top-Level-Tags"""
import struct
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
            print "EXTRACT:",tag+"@%d-%r-%d-%d"%(current_start,extended,size,current_start+size)


            f.seek(size-already_seeked,1)

            yield tag
            #yield ''.join([A,B,C,D])
        else:
            break
    f.seek(0, 2)
    print "END: %d"%(f.tell())

if __name__=="__main__":
    import sys
    if len(sys.argv) == 2:
        print list(get_Tag_seek2next(open(sys.argv[1],'rb')))
    elif len(sys.argv) == 3:
        print list(get_Tag_seek2next(open(sys.argv[1],'rb'), start=int(sys.argv[2])))
    else:
        print "Usage: python extract_TLT.py filename.mov"
