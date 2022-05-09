#!/usr/bin/env python3
import pandas as pd
import argparse

def obj2list(obj_file):
    print(obj_file)
    mesh = pd.read_csv(obj_file, sep='\s+',header=None, compression='infer', comment='#',low_memory=False)
    mesh.columns = ['type', 'x', 'y', 'z']
    v=mesh[mesh['type']=='v']
    v = v[['x','y','z']]
    f=mesh[mesh['type']=='f']
    f.columns = ['type', 'v1', 'v2', 'v3']

    v = v.copy()
    v = v.astype('float')
    v['z'] = v['z'] + 9
    v['xyz'] = '['+v['x'].map(str)+','+v['y'].map(str)+','+v['z'].map(str)+']'
    v = v['xyz']


    ff = pd.concat([f['v1'].str.split('//', expand=True),f['v2'].str.split('//', expand=True),f['v3'].str.split('//', expand=True)], axis=1)
    ff.columns=['v1','vt1','v2','vt2','v3','vt3']
    ff= ff[['v1','v2','v3']]
    ff = ff.astype('int')
    ff = ff-1
    ff= ff.copy()
    ff['index'] = '['+ff['v1'].map(str)+','+ff['v2'].map(str)+','+ff['v3'].map(str)+']'
    ff = ff['index']

    json_print = '['+ str(v.tolist()).replace("'","") + ',' + '\n' + str(ff.tolist()).replace("'","") + ']'
    return json_print

def main(args):

    n = int(len(args.filename))
    json_all = '['
    for i in range(n):
        file1 = args.filename[0]
        json_print= obj2list(args.filename[i])
        json_all = json_all + json_print1 +',' + '\n'
    json_all = json_all + ']'
    savejson=open(f'{args.output}._mesh.json','w')
    print(json_all,file=savejson)
    json.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="file1 file2 file3 file4", type=str, default=[], nargs='+')
    parser.add_argument("-o", "--output", help="directory to save files", type=str,default='output')
    args = parser.parse_args()
    main(args)
#result = pd.DataFrame(columns=['p1', 'p2'])


#result.to_csv('C:/Users/jizhi1/Desktop/result.txt',sep='\t',header=True,index=False)
