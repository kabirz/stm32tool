#!/usr/bin/env python3
import stm32tool as openmv
import argparse
import pygame
import os
import time
from .data import hello_world


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='script file')
    parser.add_argument('-o', '--out', default='image', help='capture image output dictory')
    args = parser.parse_args()

    cam = openmv.OpenMV()

    if not cam.connect():
        exit()
    # pygame init
    pygame.init()

    cam.stop_script()
    cam.fb_enable(True)
    if args.file:
        data = open(args.file, 'r').read()
    else:
        data = hello_world
    cam.exec_script(data)

    running = True
    Clock = pygame.time.Clock()
    pygame.display.set_caption('OpenMV Camera')
    Clock.tick(100)
    frame_count = 1
    frame_size = None

    while running:
        fb = cam.fb_dump()
        if fb != None:
            # create image from RGB888
            image = pygame.image.frombuffer(fb[2].flat[0:], (fb[0], fb[1]), 'RGB')
            screen = pygame.display.set_mode(fb[:2])
            fps = Clock.get_fps()
            screen.blit(image, (0, 0))
            pygame.display.set_caption('OpenMV({}x{}, Fps:{:0.2f})'.format(*fb[:2], fps))

            pygame.display.flip()
            frame_count += 1
            frame_size = fb[:2]
            Clock.tick(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c and frame_size:
                    dir_name = os.path.abspath(args.out)
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name)
                    file_name = os.path.join(dir_name, '{}x{}-{}_{}.png'.format(*frame_size, time.strftime("%H-%M-%S"), frame_count))
                    pygame.image.save(image, file_name)
                    print('save image: {}'.format(file_name))

    pygame.quit()
    cam.stop_script()
    cam.disconnect()
