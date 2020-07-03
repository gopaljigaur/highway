from pathlib import Path
import random
import cv2 as cv
import filetype as flt
import os, os.path
import numpy as np
import subprocess
import sys, getopt, shutil
from PIL import Image, ImageFont, ImageDraw
import re
from pydub.utils import mediainfo
from datetime import datetime
import pytz
import base64

def format_time(total_duration):
    hrs_req=False
    hours = int(total_duration/3600)
    if hours>0:
        hrs_req=True
    minutes = int((total_duration - 3600*hours)/60)
    seconds = int(round(total_duration%60))

    
    if(len(str(seconds))!=2):
        seconds = '0'+str(seconds)
    if(len(str(minutes))!=2):
        minutes = '0'+str(minutes)
    if(hrs_req):
        if(len(str(hours))!=2):
            hours = '0'+str(hours)
    if(hrs_req):
        format_dur = str(hours)+':'+str(minutes)+':'+str(seconds)
    else:
        format_dur = str(minutes) + ':' + str(seconds)

    return(format_dur,hrs_req)

def rounded_rectangle(src, top_left, bottom_right, radius=1, color=255, thickness=1, line_type=cv.LINE_AA):

    #  corners:
    #  p1 - p2
    #  |     |
    #  p4 - p3

    bottom_right = (bottom_right[1],bottom_right[0])
    p1 = top_left
    p2 = (bottom_right[1], top_left[1])
    p3 = (bottom_right[1], bottom_right[0])
    p4 = (top_left[0], bottom_right[0])

    height = abs(bottom_right[0] - top_left[1])

    if radius > 1:
        radius = 1

    corner_radius = int(radius * (height/2))

    if thickness < 0:

        #big rect
        top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
        bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

        top_left_rect_left = (p1[0], p1[1] + corner_radius)
        bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

        top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
        bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

        all_rects = [
        [top_left_main_rect, bottom_right_main_rect], 
        [top_left_rect_left, bottom_right_rect_left], 
        [top_left_rect_right, bottom_right_rect_right]]

        [cv.rectangle(src, rect[0], rect[1], color, thickness) for rect in all_rects]

    # draw straight lines
    cv.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
    cv.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
    cv.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
    cv.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, color ,thickness, line_type)
    cv.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, color , thickness, line_type)
    cv.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,   color , thickness, line_type)
    cv.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,  color , thickness, line_type)

    return src

def crop_img(img,thr):
    try:
        img_gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(img_gray,thr,255,cv.THRESH_BINARY)
        contours,_ = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_NONE)
        areas = [cv.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        x,y,w,h = cv.boundingRect(cnt)
        img = img[y:y+h,x:x+w]
        if((img.shape[1]/img.shape[0])==(1920/1080)):
            return(img)
        elif((img.shape[1]/img.shape[0])>(1920/1080)):
            wid = int(img.shape[0]*(1920/1080))
            left_lim = int((img.shape[1] - wid)/2)
            img = img[:,left_lim:left_lim+wid]
            return(img)
        else:
            het = int(img.shape[1]*(1080/1920))
            up_lim = int((img.shape[0] - het)/2)
            img = img[up_lim:up_lim+het,:]
            return(img)
    except:
        return(img)


def main(argv):
    no_compress = False
    capture_duration = 3
    only_thumb = False
    tag_edit = False
    noloop=False
    noemail=False
    
    try:
        opts, args = getopt.getopt(argv,"d:telcn",["duration=","thumb","tags","noloop","nocompress","noemail"])
    except getopt.GetoptError:
        print('input error')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-d','--duration'):
            capture_duration = arg
        if opt in ('-t','--thumb'):
            only_thumb = True
        if opt in ('-e','--tags'):
            tag_edit = True
        if opt in ('-l','--noloop'):
            noloop = True
        if opt in ('-c','--nocompress'):
            no_compress = True
        if opt in ('-n','--noemail'):
            noemail=True
    
    tz_in = pytz.timezone('Asia/Kolkata')
    datetime_in = datetime.now(tz_in)
    dt_string = datetime_in.ctime()
    if not noemail:
        subprocess.call(['sendemail', '-f', 'rpinotify5@gmail.com', '-t', 'gopaljigaur@gmail.com', '-u', 'Helper Script Started', '-m', 'Helper Script Started at : '+dt_string, '-s', 'smtp.gmail.com:587', '-xu', 'rpinotify5@gmail.com', '-xp', 'Ljgad#94912'])
    
    cwd=Path('C:/inetpub/wwwroot')
    #cwd=Path('D:/Github/highway')
    vidpath = Path.joinpath(cwd,'videos')
    thumbpath = Path.joinpath(cwd,'thumbs')
    tagPath = Path.joinpath(cwd,'files')
    runpath = Path('C:/inetpub/generate')
    
    itr = Path.iterdir(vidpath)
    itr1 = Path.iterdir(vidpath)
    itr2 = Path.iterdir(thumbpath)
    lis_prev = list()
    lis = list()
    thumblis=list()
    images_present = list()
    to_be_deleted = list()

    if(os.path.isfile(Path.joinpath(runpath,'vidlist.txt'))):
        f = open(Path.joinpath(runpath,'vidlist.txt'))
        cont = f.readlines()
        #remove \n
        for i in cont:
            lis_prev.append(i[:-1])
        f.close()
    elif(os.path.isfile(Path.joinpath(runpath,'vidlist.txt.bkp'))):
        cont = f.readlines()
        #remove \n
        for i in cont:
            lis_prev.append(i[:-1])
        f.close()
    else:
        print("neither files found...winging it")
    #Switch

    for i in itr:
        if(str(i)[-3:] in ('mp4')):
            if(str(i)[-9:]=='\loop.mp4') or (str(i)[-10:]=='\input.avi') or (str(i)[-9:]=='_temp.mp4'):
                continue
            else:
                lis.append(str(i))     

    for i in itr1:
        if(str(i)[-3:] in ('m4v','mov','mkv','avi')):
            if (str(i)[-10:]=='\input.avi'):
                continue
            else:
                lis.append(str(i))
    
    for i in itr2:
        if str(i)[-3:]in ('fig','php'):
            continue
        to_be_deleted.append(str(i))
    #tag test

    f_try = open(Path.joinpath(tagPath,'tags.txt'),'r')
    cont = f_try.readlines()
    if(len(cont)!=0):
        if(os.path.isfile(Path.joinpath(runpath,'tags.txt.bkp'))):
            os.remove(Path.joinpath(runpath,'tags.txt.bkp'))
        if(os.path.isfile(Path.joinpath(tagPath,'tags.txt'))):
            shutil.copyfile(Path.joinpath(tagPath,'tags.txt'),Path.joinpath(runpath,'tags.txt.bkp'))
    if(len(cont)!=len(lis)):
        tag_edit=True
        
    if(tag_edit):
        fl = open(Path.joinpath(tagPath,'tags.txt'),'r')
        cont = fl.readlines()
        fl.close()
        if(len(cont)==0):
            fl = open(Path.joinpath(tagPath,'tags.txt'),'w+')
            print('Need to generate all tags..')
            print('Input tags for each video line by line...')
            for i in range(1,len(lis)+1):
                print(i,end=' - ')
                print(lis[i-1][lis[i-1].rindex('\\')+1:-4])
                print('Tags : ',end='')
                x = input()
                fl.write(x)
                fl.write('\n')
            print('written')
            fl.close()
            
        elif(len(cont)!=len(lis)):
            fl =open(Path.joinpath(tagPath,'tags.txt'),'r+')
            content = fl.readlines()
            fl.close()
            print('Number of tags mismatch. Correction Mode')
            for i in range(0,len(lis)):
                print((i+1),end=' - ')
                print(lis[i][lis[i].rindex('\\')+1:-4],end=' -> ')

                if(lis[i] not in lis_prev):
                    print('**no tags**')
                    continue
                else:
                    print(lis_prev.index(lis[i]))
                    print(content[lis_prev.index(lis[i])])
            fl =open(Path.joinpath(tagPath,'tags.txt'),'w+')
            for i in range(0,len(lis)):
                if(lis[i] in lis_prev):
                    #get tags from that index
                    t=lis[i]
                    u=lis_prev.index(t)
                    v=content[u]
                    fl.write(v)
                else:
                    print(lis[i])
                    print('Input Tags : ',end='')
                    inserted_tags = input()
                    fl.write(inserted_tags)
                    fl.write('\n')

            fl.close()
        elif(len(cont)==len(lis)):
            fl = open(Path.joinpath(tagPath,'tags.txt'),'r+')
            content = fl.readlines()
            fl.close()
            print('All Tags in Place. Edit Mode')
            fl = open(Path.joinpath(tagPath,'tags.txt'),'w+')
            for i in range(1,len(lis)+1):
                print(i,end=' - ')
                print(lis[i-1][lis[i-1].rindex('\\')+1:-4])
            
            while(True):
                print('Enter the video number (q to stop)')

                vid_num = input()
                if(vid_num=='q'):
                    for k in content_upper:
                        fl.write(k)
                    
                    fl.close()
                    print('written.')
                    break
                else:
                    vid_num = int(vid_num)
                print('Current Tags : ',end='')
                print(content[vid_num-1])

                print('Enter New Tags : ',end='')
                new_tags = input()
                content_upper = content[:vid_num-1]
                
                content_upper.append(new_tags+'\n')
                for j in content[vid_num:]:
                    content_upper.append(j)
                    
                content =content_upper[:]

        else:
            print("Tag generation error")
        
    #video compression
    vid_cmp_num=0
    last_mail_time = 0
    if not no_compress:
        for i in lis:
            print(i,end=' : ')
            info = mediainfo(i)
            bitr = int(info['bit_rate'])
            vi = cv.VideoCapture(i)
            fp = vi.get(cv.CAP_PROP_FPS)
            vi.release()
            print(fp)
            if(bitr>700000) or (fp>35):
                print('will be compressed')
                vid_cmp_num = vid_cmp_num+1
        if(vid_cmp_num>1):   
            datetime_in = datetime.now(tz_in)
            dt_string = datetime_in.ctime()
            if not noemail:
                subprocess.call(['sendemail', '-f', 'rpinotify5@gmail.com', '-t', 'gopaljigaur@gmail.com', '-u', 'Compression Started', '-m', 'Compression of '+str(vid_cmp_num)+' videos started at : '+dt_string, '-s', 'smtp.gmail.com:587', '-xu', 'rpinotify5@gmail.com', '-xp', 'Ljgad#94912'])
            last_mail_time = int(datetime_in.timestamp())
        to_be_comp = vid_cmp_num
        for i in lis:
            print(i)
            info = mediainfo(i)
            bitr = int(info['bit_rate'])
            vi = cv.VideoCapture(i)
            fp = vi.get(cv.CAP_PROP_FPS)
            vi.release()
            if(bitr>700000) or (fp>35):
                print('will be compressed')
                outfile = str(i)[:-4]+'_temp.mp4'
                subprocess.call(['ffmpeg','-y','-i', str(i), '-c:v', 'libx264','-c:a','aac','-b:v','600k','-filter:v','fps=fps=25','-b:a','64k', outfile])
                os.remove(str(i))
                #remove original
                os.rename(outfile,i)
                to_be_comp = to_be_comp-1
                datetime_in = datetime.now(tz_in)
                if (int(datetime_in.timestamp()) - last_mail_time) >= 43200:
                    dt_string = datetime_in.ctime()
                    if not noemail:
                        subprocess.call(['sendemail', '-f', 'rpinotify5@gmail.com', '-t', 'gopaljigaur@gmail.com', '-u', 'Compression Update', '-m', 'Compression of '+str(vid_cmp_num-to_be_comp)+' videos finished. Compression of '+str(to_be_comp)+' videos remaining at : '+dt_string, '-s', 'smtp.gmail.com:587', '-xu', 'rpinotify5@gmail.com', '-xp', 'Ljgad#94912'])
                    last_mail_time = int(datetime_in.timestamp())
                    
                #rename temp

    if not no_compress:
        if(vid_cmp_num>1):
            datetime_in = datetime.now(tz_in)
            dt_string = datetime_in.ctime()
            if not noemail:
                subprocess.call(['sendemail', '-f', 'rpinotify5@gmail.com', '-t', 'gopaljigaur@gmail.com', '-u', 'Compression Finished', '-m', 'Compression of '+str(vid_cmp_num)+' videos finished at : '+dt_string, '-s', 'smtp.gmail.com:587', '-xu', 'rpinotify5@gmail.com', '-xp', 'Ljgad#94912'])
        
    tag_file = open(Path.joinpath(tagPath,'tags.txt'),'r+')
    tag_line = tag_file.readlines()
    tag_file.close()
    tag_lis=list()
    
    for i in tag_line:
        tag_lis.append(i[:-1])
    tag_list = 'var tag_list=['
    id_list  = 'var ids=['
    vid_list = 'var vid_list=['
    mime_list = 'var mime_list=['
    shuff_lis = lis[:]
    random.shuffle(shuff_lis)
    for i in range(1,len(shuff_lis)+1):
        id_list+='"'+str(i)+'",'
        vid_list+='"'+str(base64.b64encode(('videos/'+shuff_lis[i-1][shuff_lis[i-1].rindex('\\')+1:]).encode('utf-8')))[2:-1]+'",'
        tag_list+='"'+str(base64.b64encode(tag_lis[lis.index(shuff_lis[i-1])].encode('utf-8')))[2:-1]+'",'
        if(flt.guess(shuff_lis[i-1]).mime=='video/quicktime'):
            mime_list+='"'+str(base64.b64encode(('video/mp4').encode('utf-8')))[2:-1]+'",'
        else:
            mime_list+='"'+str(base64.b64encode(flt.guess(shuff_lis[i-1]).mime.encode('utf-8')))[2:-1]+'",'

    vid_list= vid_list[:-1]+']'
    id_list = id_list[:-1]+']'
    mime_list = mime_list[:-1]+']'
    tag_list = tag_list[:-1]+']'
        
    if not only_thumb and not noloop:
        # now loop generation
        fourcc = cv.VideoWriter_fourcc(*'XVID')

        out = cv.VideoWriter(str(Path.joinpath(tagPath,'input.avi')),fourcc, 30.0, (1920,1080))

        temp_lis=list()
        for i in lis:
            temp_lis.append(i)
        random.shuffle(temp_lis)
        
        for i in temp_lis[:8]:    
            vid = cv.VideoCapture(i)
            print(i)
            fps = vid.get(cv.CAP_PROP_FPS)
            total_frames = vid.get(cv.CAP_PROP_FRAME_COUNT)
            num_of_frames = int(capture_duration*fps)
            fram_to_gt = random.randint(int(total_frames/1.5),int(total_frames-num_of_frames-20))
            vid.set(1,fram_to_gt)
            
            count =0
            while(count<num_of_frames):
                count+=1
                ret, frame = vid.read()
                if ret==True:
                    #removal of borders
                    frame = crop_img(frame,5)
                    frame = cv.resize(frame,(1920,1080))
                    out.write(frame)
                else:
                    break
        
         
        # Release everything if job is finished

        out.release()
        cv.destroyAllWindows()

        if(os.path.isfile(str(Path.joinpath(tagPath,'loop.mp4')))):
            os.remove(str(Path.joinpath(tagPath,'loop.mp4')))
        subprocess.call(['ffmpeg','-y', '-i', str(Path.joinpath(tagPath,'input.avi')), '-c:v', 'libx264','-b:v','800k','-filter:v','fps=fps=25', str(Path.joinpath(tagPath,'loop.mp4'))])
        os.remove(str(Path.joinpath(tagPath,'input.avi')))
    

    # generating thumbnails and index now

    print('Cleanup...')

    thum_gen = [True]*len(lis)
        
    for i in to_be_deleted:
        if (str(Path.joinpath(vidpath,i[i.rindex('\\')+1:-4])) in lis) or (str(Path.joinpath(vidpath,i[i.rindex('\\')+1:-6])) in lis):
            images_present.append(i)
        
    for i in to_be_deleted:
        if i not in images_present:
            os.remove(i)
            print('removed ',i)

    for i in lis:
        if (str(Path.joinpath(thumbpath,i[i.rindex('\\')+1:]+'.jpg')) in images_present) or (Path.joinpath(thumbpath,i[i.rindex('\\')+1:]+'_1.jpg') in images_present) or (Path.joinpath(thumbpath,i[i.rindex('\\')+1:]+'_2.jpg') in images_present) or (Path.joinpath(thumbpath,i[i.rindex('\\')+1:]+'_3.jpg') in images_present):
            thum_gen[lis.index(i)]=False
        
    if only_thumb:
        for i in range(1,len(lis)+1):
            print(i,end=' - ')
            if(os.path.isfile(str(Path.joinpath(thumbpath,lis[i-1][lis[i-1].rindex('\\')+1:]))+'.jpg')):
                print(lis[i-1][lis[i-1].rindex('\\')+1:-4])

            else:
                print('**no thumb**',end=' ')
                print(lis[i-1][lis[i-1].rindex('\\')+1:-4],end=' ')
                print('**no thumb**')
                
        num_regex = "^([0-9]+)-([0-9]+)$"
    
        print('enter inputs one by one. Type q to stop entering')

        while(True):
            lol=input()
            if(lol=='q'):
                break
            
            if(lol=='all'):
                thum_gen=[True]*len(lis)
                break

            found_matches = re.findall(num_regex,lol)

            if(len(found_matches)>0):
                if(len(found_matches[0])==2):
                    for k in range(int(found_matches[0][0]),int(found_matches[0][1])+1):
                        thum_gen[k]=True
                    continue
            thum_gen[int(lol)-1]=True

    if(thum_gen.count(True)>0):
        print('Thumbnail generation required')
    else:
        print('Generating only JS')

    file = open(str(Path.joinpath(cwd,'js/lang/en.js')),'w+')
    content = id_list+';'+vid_list+';'+mime_list+';'+tag_list+';'
    file.write(content)
    file.close()

    fontpath = os.path.join("D:/Github/highway/Roboto-Medium.ttf")
    
    font = ImageFont.truetype(fontpath, 20)

    seek = 0
    keylist = dict()
    keylist[ord('x')] = -10
    keylist[ord('c')] = -5
    keylist[ord('v')] = -2
    keylist[ord('b')] = 2
    keylist[ord('n')] = 5
    keylist[ord('m')] = 10

    same=False
    
    if only_thumb:
        print('======Instructions=======')
        print('Press \'Y\' to accept thumbnail')
        print('Keys to move around the video : ')
        print('\'X\' -> -10 seconds')
        print('\'C\' -> -5 seconds')
        print('\'V\' -> -2 seconds')
        print('\'B\' -> +2 seconds')
        print('\'N\' -> +5 seconds')
        print('\'M\' -> +10 seconds')
        print('\'Z\' -> New mapping')
        print('\',\' -> Show all mappings')
    for i in lis:
        key = ord('n')
        cur_ind = lis.index(i)
        img = i[i.rindex('\\')+1:]+'.jpg'
        if(thum_gen[cur_ind]):
            vid = cv.VideoCapture(i)
            fps = vid.get(cv.CAP_PROP_FPS)
            total_frames = vid.get(cv.CAP_PROP_FRAME_COUNT)
            res_string = ''
            resolution = vid.get(cv.CAP_PROP_FRAME_HEIGHT)
            num_of_frames = int(capture_duration*fps)
            total_duration = total_frames/fps
            format_dur,hrs_req = format_time(total_duration)
            if(resolution>=900):
                res_string = '1080p'
            elif(650<=resolution<900):
                res_string = '720p'
            elif(420<=resolution<650):
                res_string = '480p'
            elif(300<=resoltion<420):
                res_string = '360p'
            elif(200<=resolution<300):
                res_string = '240p'
            elif(resolution<200):
                res_string = '144p'

            print(res_string)
                
            
            print('duration (H:M:S) = '+ format_dur)
            
            while(key!=ord('y')):
                if not same:
                    if seek==0:
                        fram_to_gt = random.randint(int(10*fps),int(total_frames-num_of_frames-10))

                    else:
                        fram_to_gt+= seek*fps
                        if(seek>0):
                            print('+',end='')
                        print(seek,' seconds')
                if same:
                    same= False
                print(format_time(int(fram_to_gt/fps))[0],' of ',format_dur)
                seek=0
                if(fram_to_gt<=0):
                    fram_to_gt=1
                    print('reached beginning of video file')
                if(fram_to_gt>=total_frames):
                    fram_to_gt = total_frames-1
                    print('reached end of video file')
                    
                vid.set(1,fram_to_gt)
                
                ret, frame = vid.read()
                frame = crop_img(frame,35)
                frame = cv.resize(frame,(711,400))

                if(res_string == '1080p'):
                    frame = rounded_rectangle(frame, (610,22),(673,50),color=(255,255,255),radius=0.2,thickness=-1)
                else:
                    frame = rounded_rectangle(frame, (620,22),(673,50),color=(255,255,255),radius=0.2,thickness=-1)
                
                if(hrs_req):
                    frame = rounded_rectangle(frame, (590,348),(673,376),color=(0,0,0),radius=0.2,thickness=-1)
                else:
                    frame = rounded_rectangle(frame, (616,348),(673,376),color=(0,0,0),radius=0.2,thickness=-1)

                img_pil = Image.fromarray(frame)
                draw = ImageDraw.Draw(img_pil)
                if(hrs_req):
                    draw.text((594,350),format_dur,font=font,fill=(255,255,255))
                else:
                    draw.text((620,350),format_dur,font=font,fill=(255,255,255))

                if(res_string == '1080p'):
                    draw.text((614,24),res_string,font=font,fill=(140,140,140))
                else:
                    draw.text((625,24),res_string,font=font,fill=(140,140,140))

                frame = np.array(img_pil)
            
                print('((frame ',fram_to_gt,'of ',end='')
                print(vid.get(cv.CAP_PROP_FRAME_COUNT),' frames.))')
            
                if only_thumb:
                    cv.imshow(img,frame)
                
                    key = cv.waitKey(15000)

                    if key==ord('y'):
                        cv.imwrite(str(Path.joinpath(thumbpath,img)), frame)
                        print('saved ',img)
                    
                    elif key in keylist.keys():
                        seek = keylist[key]
                    elif key==ord('z'):
                        print('Input the value (in seconds) to seek : ',end='')
                        seek = float(input())
                        print('Input the key to assign (Except \'Y\' and \'Z\')')
                        key1 = input()
                        if(key1.lower()=='b'):
                            keylist[ord('v')]=-seek
                        if(key1.lower()=='n'):
                            keylist[ord('c')]=-seek
                        if(key1.lower()=='m'):
                            keylist[ord('x')]=-seek
                        if(key1.lower()=='v'):
                            keylist[ord('b')]=-seek
                        if(key1.lower()=='c'):
                            keylist[ord('n')]=-seek
                        if(key1.lower()=='x'):
                            keylist[ord('m')]=-seek

                        keylist[ord(key1)]=seek
                    
                    if(key==ord(',')):
                        print('')
                        for lm in keylist.keys():
                            print(chr(lm),' : ',keylist[lm],' seconds')
                        same = True
                        print('')
                        
                        
                    cv.destroyAllWindows()

                else:
                    cv.imwrite(str(Path.joinpath(thumbpath,img)), frame)
                    print('saved ',img)
                    key = ord('y')
                    
                
        
    print('Saved lang.js')
    f_try = open(Path.joinpath(tagPath,'tags.txt'),'r')
    cont = f_try.readlines()

    if(len(cont)==len(lis)):
        if(os.path.isfile(Path.joinpath(runpath,'vidlist.txt.bkp'))):
            os.remove(Path.joinpath(runpath,'vidlist.txt.bkp'))
        if(os.path.isfile(Path.joinpath(runpath,'vidlist.txt'))):
            shutil.copyfile(Path.joinpath(runpath,'vidlist.txt'),Path.joinpath(runpath,'vidlist.txt.bkp'))
        f = open(Path.joinpath(runpath,'vidlist.txt'),'w+')
        for i in lis:
            f.write(i+'\n')
        f.close()
    
    if(os.path.isfile(Path.joinpath(runpath,'vidlist.txt.bkp'))):
        os.remove(Path.joinpath(runpath,'vidlist.txt.bkp'))
    f_try = open(Path.joinpath(tagPath,'tags.txt'),'r')
    cont = f_try.readlines()
    if(len(cont)!=0):
        if(os.path.isfile(Path.joinpath(runpath,'tags.txt.bkp'))):
            os.remove(Path.joinpath(runpath,'tags.txt.bkp'))
    lis=list()
    #subprocess.call(['powershell','Copy-Item', '-Exclude', '*.mp4', 'C:/inetpub/wwwroot/*', '-Recurse', 'C:/inetpub/bkup', '-passThru', '-force'])
    datetime_in = datetime.now(tz_in)
    dt_string = datetime_in.ctime()
    if not noemail:
        subprocess.call(['sendemail', '-f', 'rpinotify5@gmail.com', '-t', 'gopaljigaur@gmail.com', '-u', 'Helper Script Ended', '-m', 'Helper script ended at : '+dt_string, '-s', 'smtp.gmail.com:587', '-xu', 'rpinotify5@gmail.com', '-xp', 'Ljgad#94912'])
        
if __name__ == "__main__":
    main(sys.argv[1:])
                         
