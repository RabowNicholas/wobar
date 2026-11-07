import sys, bpy
a=bpy.data.images.load(sys.argv[-2]); b=bpy.data.images.load(sys.argv[-1])
pa=list(a.pixels); pb=list(b.pixels)
for ch,nm in enumerate("RGBA"):
    xs=pa[ch::4]; ys=pb[ch::4]
    print("CH",nm,"meandiff %.3f"%(sum(abs(x-y) for x,y in zip(xs,ys))/len(xs)*255), "meanA %.3f meanB %.3f"%(sum(xs)/len(xs), sum(ys)/len(ys)))
