#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car

Usage:
    manage.py (drive) [--model=<model>] [--js] [--type=(linear|categorical)] [--camera=(single|stereo)] [--meta=<key:value> ...] [--myconfig=<filename>]
    manage.py (train) [--tubs=tubs] (--model=<model>) [--type=(linear|inferred|tensorrt_linear|tflite_linear)]

Options:
    -h --help               Show this screen.
    --js                    Use physical joystick.
    -f --file=<file>        A text file containing paths to tub files, one per line. Option may be used more than once.
    --meta=<key:value>      Key/Value strings describing describing a piece of meta data about this drive. Option may be used more than once.
    --myconfig=filename     Specify myconfig file to use. 
                            [default: myconfig.py]
"""
from docopt import docopt
import donkeycar as dk
from donkeycar.parts.camera import PiCamera
from donkeycar.parts.controller import LocalWebController

def drive(cfg, model_path=None, use_joystick=False, model_type=None,
          camera_type='single', meta=[]):
    V = dk.Vehicle()

    #初始化相機模組
    cam = PiCamera()
    V.add(cam, outputs=['cam/image_array']) #相機的輸出為web控制的輸入

    #初始化Web模組
    ctr = LocalWebController()
    V.add(ctr, inputs=['cam/image_array'],
               outputs=['user/angle'],
               threaded=True) #網頁執行在單獨的執行序
    
    #新增轉向模組

    #新增油門模組

    V.start()

if __name__ == "__main__":
    args = docopt(__doc__)
    cfg = dk.load_config(myconfig=args['--myconfig'])

    if args['drive']:
        model_type = args['--type']
        camera_type = args['--camera']
        drive(cfg, model_path=args['--model'], use_joystick=args['--js'],
              model_type=model_type, camera_type=camera_type,
              meta=args['--meta'])
    elif args['train']:
        print('Use python train.py instead.\n')