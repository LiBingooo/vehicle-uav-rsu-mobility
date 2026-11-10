"""Build a mixed traffic replay from a locally obtained highD recording."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from vec_mobility.preprocess import build_processed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracks',type=Path,required=True)
    parser.add_argument('--recording-meta',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seed',type=int,default=48)
    args = parser.parse_args()
    data = build_processed(args.tracks,args.recording_meta,args.output,args.seed)
    print(f'Created {args.output}: {len(data)} vehicle observations')


if __name__=='__main__':
    main()
