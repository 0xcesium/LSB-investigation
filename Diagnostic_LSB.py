#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# --------------------------------
#	LSB parser by Cs[133]
#	Extraction | Insertion
#	GPL Licence : (v1.3)
# --------------------------------
#
# CAUTION : Could possibly makes you puke. 
# It's ugly.
# Author: Cesium133


from PIL import Image
import binascii
import base64
import sys
import os
try:
	import hackercodecs
except:
	print "[-] You need to download the hackercodecs.py API in order to run this script."
	sys.exit(">>> wget https://raw.githubusercontent.com/jdukes/hackercodecs/master/hackercodecs/__init__.py && mv __init__.py hackercodecs.py")


# Colors consts
SUCCESS = '\033[94m'
ERROR   = '\033[91m'
INFO	= '\033[93m'
END     = '\033[0m'

RED	= '\33[31mRED\33[0m'
GREEN	= '\33[32mGREEN\33[0m'
BLUE	= '\33[36mBLUE\33[0m'
RGB	= '\33[31mRED\33[0m \33[32mGREEN\33[0m \33[36mBLUE\33[0m'

p_RED 	= 0
p_GREEN	= 1
p_BLUE	= 2
p_RGB	= -1

########################
#         Usage        #
########################

def __usage():
	print "Usage:\n\n" + INFO + \
"Extraction:\n\t" + END + sys.argv[0] + " -e|--extract <image>\n\n" + INFO + \
"Insertion:\n\t" + END + sys.argv[0] + " -i<OPTION> <image> -enc <encryption-format> <MSG>\n\n" + INFO + \
"Insertion types:\n\t" + END + \
"[-idr|--insert-diag-red] \tDiagonal. " + RED + \
"\n\t[-idg|--insert-diag-green] \tDiagonal. " + GREEN + \
"\n\t[-idb|--insert-diag-blue] \tDiagonal. " + BLUE + \
"\n\t[-ida|--insert-diag-rgb] \tDiagonal. " + RGB + \
"\n\t[-ir|--insert-red] \t\tFirst 3 lines. " + RED + \
"\n\t[-ig|--insert-green] \t\tFirst 3 lines. " + GREEN + \
"\n\t[-ib|--insert-blue] \t\tFirst 3 lines. " + BLUE + \
"\n\t[-ia|--insert-rgb] \t\tFirst 3 lines. " + RGB + \
"\n\t[-ir2|--insert-2-bits-red] \tFirst 3 lines, 2 LSB. " + RED + \
"\n\t[-ig2|--insert-2-bits-green] \tFirst 3 lines, 2 LSB. " + GREEN + \
"\n\t[-ib2|--insert-2-bits-blue] \tFirst 3 lines, 2 LSB. " + BLUE + \
"\n\t[-ir3|--insert-3-bits-red] \tFirst 3 lines, 3 LSB. " + RED + \
"\n\t[-ig3|--insert-3-bits-green] \tFirst 3 lines, 3 LSB. " + GREEN + \
"\n\t[-ib3|--insert-3-bits-blue] \tFirst 3 lines, 3 LSB. " + BLUE + \
"\n\t[-ia3|--insert-3-bits-rgb] \tFirst 3 lines, 3 LSB. " + RGB + \
"\n\t[-i2r|--insert-pair-red] \t1 out of 2 pixels [even ones]. " + RED + \
"\n\t[-i2g|--insert-pair-green] \t1 out of 2 pixels [even ones]. " + GREEN + \
"\n\t[-i2b|--insert-pair-blue] \t1 out of 2 pixels [even ones]. " + BLUE + \
"\n\t[-i2a|--insert-pair-rgb] \t1 out of 2 pixels [even ones]. " + RGB + INFO +\
"\n\nMessage structure: \n\t" + END + \
	 "Max:[width|length -10] / [A-Z0-9a-z\\*^\\]]\n\t" + INFO + \
"\nEncoding formats available: \n\t" + END + \
	 'ascii85\n\t' + \
	 'base16\n\t' + \
	 'base32\n\t' + \
	 'base64\n\t' + \
         'bin\n\t' + \
         'entity\n\t' + \
         'entityhex\n\t' + \
         'morse\n\t' + \
         'rot1\n\t' + \
         'rot10\n\t' + \
         'rot11\n\t' + \
         'rot12\n\t' + \
         'rot13\n\t' + \
         'rot14\n\t' + \
         'rot15\n\t' + \
         'rot16\n\t' + \
         'rot17\n\t' + \
         'rot18\n\t' + \
         'rot19\n\t' + \
         'rot2\n\t' + \
         'rot20\n\t' + \
         'rot21\n\t' + \
         'rot22\n\t' + \
         'rot23\n\t' + \
         'rot24\n\t' + \
         'rot25\n\t' + \
         'rot3\n\t' + \
         'rot4\n\t' + \
         'rot5\n\t' + \
         'rot6\n\t' + \
         'rot7\n\t' + \
         'rot8\n\t' + \
         'rot9\n\t' + \
         'url\n\t' + \
         'yenc\n\t'
	sys.exit(1)

#####################################################
#         Translate message to insert to bin        #
#####################################################

def __TxtToBin(MSG):
	bin_msg = ''
	for C in MSG:
		cc = bin(ord(C))[2:]
		nbz = 8 - len(cc)
		if nbz == 0:
			bin_msg += cc
		else:
			bin_msg += nbz*'0' + cc

	# Adding some zeros to avoid bad insertion within the compute of RGB's LSBs (either Diagonal or Inline ones)
	if len(bin_msg) % 3 == 0:
		return bin_msg
	else:
		if len(bin_msg + '0') % 3 == 0:
			return bin_msg + '0'
		else:
			return bin_msg + '00'

####################################
#         Random image name        #
####################################

def __randName():
	name = "IMG_"
	name += os.urandom(13).encode('base64').strip().replace('/','').replace('=','')
	name += ".png"

	return name

########################################
#         Try to grab the image        #
########################################

def __imgOpen(OBJ):
	# The object to work on. [TYPE:Image]
	try:
		img = Image.open(OBJ)
	except:
		print ERROR + "\nERROR [#3]: Cannot find any " + END + OBJ + ERROR + " ... Quitting.\n" + END
		sys.exit(2)

	return img


#########################################
#	Extract Diagonal LSB from 0	#
#########################################

def __Diagonal_LSB(img,lig,color):
	EXT,trEXT = '',''
	for x in range(lig):
                pix = img.getpixel((x,x))
                p = bin(pix[color])
                EXT += p[-1]
                if len(EXT) == 8:
                        trEXT += chr(int('0b' + EXT, 2))
                        EXT = ''
	return trEXT

#################################################
#	Extract First lines 1|2 LSB 1/1 from 0	#
#################################################

def __1on1_LSB(img,col,color,COUNT):
	EXT,trEXT = '',''
	for y in range(3):
               for x in range(col):
	               pix = img.getpixel((x,y))
                       EXT += bin(pix[color])[COUNT:]
                       if len(EXT) == 8:
                       		trEXT += chr(int('0b' + EXT, 2))
                                EXT = ''
	return trEXT

###############################################
#       Extract First lines 3 LSB 1/1 from 0  #
###############################################

def __1on1_3_LSB(img,col,color):
        EXT,trEXT = '',''
        for y in range(3):
               for x in range(col):
                       pix = img.getpixel((x,y))
                       EXT += bin(pix[color])[-3:]
                       if len(EXT) > 8:
                                trEXT += chr(int('0b' + EXT[:8], 2))
                                EXT = '' + EXT[-len(EXT)+8:]
        return trEXT

#################################################
#	Exctract First lines LSB 1/2 from 0	#
#################################################

def __1on2_LSB(img,col,color):
	EXT,trEXT = '',''
	for y in range(3):
        	for x in range(col):
                        if x % 2 == 0 or x == 0:
                                pix = img.getpixel((x,y))
                                EXT += bin(pix[color])[-1]
                                if len(EXT) == 8:
                                        trEXT += chr(int('0b' + EXT, 2))
                                        EXT = ''
	return trEXT

##############################################
#         Insertion in img 1/1 OR 1/2        #
##############################################

def __insert(OBJ,MSG,COLOR,COUNT,ENC):
        img = __imgOpen(OBJ)
        lig, col = img.size
        pix = img.load()
	c,l = 0,0

        # Converts the MSG :
        # 1st) to Choosen encode
        # 2nd) to Binary
	try:
	        MSG = MSG.encode(ENC)
	        print MSG
	        bin_msg = __TxtToBin(MSG)
	except:
		if ENC == "base32":
			MSG = base64.b32encode(MSG)
			print MSG
			bin_msg = __TxtToBin(MSG)
		elif ENC == "base16":
			MSG = base64.b16encode(MSG)
			print MSG
			bin_msg = __TxtToBin(MSG)
		else:
			print MSG
			bin_msg = __TxtToBin(MSG)

        long = len(bin_msg)

        # Inserts the binary MSG
        # into the RED-LSB of IMG_Name
	# From the forst line in the TOP-LEFT_HAND CORNER
	if COLOR == p_RED:
                for x in range(long):
			if c > col:
        	                c = 0
				l += 1
			if bin_msg[x] == "0":
       	       	                pio = img.getpixel((c,l))
      	        	        if bin(pio[p_RED])[-1] == '1':
               		                pi = pio[p_RED] - 1
                       		        pix[c,l] = (pi,pio[p_GREEN],pio[p_BLUE])
               		elif bin_msg[x] == "1":
               		        pio = img.getpixel((c,l))
               		        if bin(pio[p_RED])[-1] == '0':
               		                pi = pio[p_RED] + 1
               		                pix[c,l] = (pi,pio[p_GREEN],pio[p_BLUE])
			c += COUNT

        # GREEN-LSB
        elif COLOR == p_GREEN:
                for x in range(long):
                        if c > col:
                                c = 0
                                l += 1
                        if bin_msg[x] == "0":
                                pio = img.getpixel((c,l))
                                if bin(pio[p_GREEN])[-1] == '1':
                                        pi = pio[p_GREEN] - 1
                                        pix[c,l] = (pio[p_RED],pi,pio[p_BLUE])
                        elif bin_msg[x] == "1":
                                pio = img.getpixel((c,l))
                                if bin(pio[p_GREEN])[-1] == '0':
                                        pi = pio[p_GREEN] + 1
                                        pix[c,l] = (pio[p_RED],pi,pio[p_BLUE])
			c += COUNT

        # BLUE-LSB
        elif COLOR == p_BLUE:
                for x in range(long):
                        if c > col:
                                c = 0
                                l += 1
                        if bin_msg[x] == "0":
                                pio = img.getpixel((c,l))
                                if bin(pio[p_BLUE])[-1] == '1':
                                        pi = pio[p_BLUE] - 1
                                        pix[c,l] = (pio[p_RED],pio[p_GREEN],pi)
                        elif bin_msg[x] == "1":
                                pio = img.getpixel((c,l))
                                if bin(pio[p_BLUE])[-1] == '0':
                                        pi = pio[p_BLUE] + 1
                                        pix[c,l] = (pio[p_RED],pio[p_GREEN],pi)
			c += COUNT

	# Inserts the binary MSG
        # into all LSB of IMG_Name from First line -> TOP-LEFT-HAND-CORNER
        else:
                for x in range(0, long, 3):
			if c > col:
                                c = 0
                                l += 1
			pio = img.getpixel((c,l))
			piR = pio[p_RED]
                        piG = pio[p_GREEN]
                        piB = pio[p_BLUE]
			fragment = bin_msg[x:x+3]
	                for i in range(3):
				if fragment[i] == "0":
					if i == 0:
               	                		if bin(piR)[-1] == '1':
               	                	        	piR -= 1
               	                	elif i == 1:
						if bin(piG)[-1] == '1':
               	                	        	piG -= 1
					elif i == 2:
               	                		if bin(piB)[-1] == '1':
               	                	        	piB -= 1
               			elif fragment[i] == "1":
					if i == 0:
               	                		if bin(piR)[-1] == '0':
               	                	        	piR += 1
					elif i == 1:
               	                		if bin(piG)[-1] == '0':
               	                	        	piG += 1
					elif i == 2:
               	                		if bin(piB)[-1] == '0':
               	                	        	piB += 1
			pix[c,l] = (piR,piG,piB)
			c += COUNT

	Name = __randName()
        img.save(Name)

        print SUCCESS + "[+] MSG successfully hidden in " + END + Name


#####################################################
#         Insertion in img 1/1 in 2 OR 3 LSB        #
#####################################################

def __insert_23_(OBJ,MSG,COLOR,COUNT,ENC,LSB):
        img = __imgOpen(OBJ)
        lig, col = img.size
        pix = img.load()
	c,l = 0,0

        # Converts the MSG :
        # 1st) to Choosen encode
        # 2nd) to Binary
	try:
	       MSG = MSG.encode(ENC)
	       print MSG
	       bin_msg = __TxtToBin(MSG)
	except:
		if ENC == "base32":
			MSG = base64.b32encode(MSG)
			print MSG
			bin_msg = __TxtToBin(MSG)
		elif ENC == "base16":
			MSG = base64.b16encode(MSG)
			print MSG
			bin_msg = __TxtToBin(MSG)
		else:
			print MSG
			bin_msg = __TxtToBin(MSG)

        long = len(bin_msg)

        # Inserts the binary MSG
        # into the 2|3 RED-LSB of IMG_Name
	# From the forst line in the TOP-LEFT_HAND CORNER
	if COLOR == p_RED:
                for x in range(0,long,LSB):
			if c > col:
        	                c = 0
				l += 1
			pio = img.getpixel((c,l))
			piR = pio[p_RED]
			piG = pio[p_GREEN]
			piB = pio[p_BLUE]
			for i in range(LSB):
				cpt = -LSB + i
				lsb = bin(piR)[cpt]
				if bin_msg[x + i] == "0":
					if lsb == '1':
      		        		        if cpt == -3:
							piR -= 4
						elif cpt == -2:
							piR -= 2
						elif cpt == -1:
							piR -= 1
       				elif bin_msg[x + i] == "1":
					if lsb == '0':
               			        	if cpt == -3:
       	                                        	piR += 4
               	                        	elif cpt == -2:
                       	                	        piR += 2
                               	        	elif cpt == -1:
                                       		        piR += 1
			pix[c,l] = (piR,piG,piB)
			c += COUNT

        # 2|3 GREEN-LSB
        elif COLOR == p_GREEN:
                for x in range(0,long,LSB):
                        if c > col:
                                c = 0
                                l += 1
			pio = img.getpixel((c,l))
                        piR = pio[p_RED]
                        piG = pio[p_GREEN]
                        piB = pio[p_BLUE]
                        for i in range(LSB):
				cpt = -LSB + i
                                lsb = bin(piG)[cpt]
                                if bin_msg[x + i] == "0":
                                        if lsb == '1':
                                                if cpt == -3:
                                                        piG -= 4
                                                elif cpt == -2:
                                                        piG -= 2
                                                elif cpt == -1:
                                                        piG -= 1
                                elif bin_msg[x + i] == "1":
                                        if lsb == '0':
                                                if cpt == -3:
                                                        piG += 4
                                                elif cpt == -2:
                                                        piG += 2
                                                elif cpt == -1:
                                                        piG += 1
                        pix[c,l] = (piR,piG,piB)
			c += COUNT

        # 2|3 BLUE-LSB
        elif COLOR == p_BLUE:
                for x in range(0,long,LSB):
                        if c > col:
                                c = 0
                                l += 1
			pio = img.getpixel((c,l))
                        piR = pio[p_RED]
                        piG = pio[p_GREEN]
                        piB = pio[p_BLUE]
                        for i in range(LSB):
				cpt = -LSB + i
                                lsb = bin(piB)[cpt]
                                if bin_msg[x + i] == "0":
                                        if lsb == '1':
                                                if cpt == -3:
                                                        piB -= 4
                                                elif cpt == -2:
                                                        piB -= 2
                                                elif cpt == -1:
                                                        piB -= 1
                                elif bin_msg[x + i] == "1":
                                        if lsb == '0':
                                                if cpt == -3:
                                                        piB += 4
                                                elif cpt == -2:
                                                        piB += 2
                                                elif cpt == -1:
                                                        piB += 1
			pix[c,l] = (piR,piG,piB)
			c += COUNT

	# Inserts the binary MSG
        # into all 3 LSB of each color in IMG_Name from First line -> TOP-LEFT-HAND-CORNER
        else:
		for i in range(9):
			if len(bin_msg) % 9 == 0:
				long = len(bin_msg)
				break
			else:
				bin_msg += i*'0'

                for x in range(0, long, 9):
			if c > col:
                                c = 0
                                l += 1
			pio = img.getpixel((c,l))
			piR = pio[p_RED]
                        piG = pio[p_GREEN]
                        piB = pio[p_BLUE]
			fragment = bin_msg[x:x+9]
			cptR = bin(piR)[-3:]
			cptG = bin(piG)[-3:]
			cptB = bin(piB)[-3:]
			for r in range(3):
				if fragment[r] == "0":
					if cptR[r] == "1":
						if r == 0:
							piR -= 4
						elif r == 1:
							piR -= 2
						elif r == 2:
							piR -= 1
				elif fragment[r] == "1":
					if cptR[r] == "0":
                                                if r == 0:
                                                        piR += 4
                                                elif r == 1:
                                                        piR += 2
                                                elif r == 2:
                                                        piR += 1
			for g in range(3,6):
				if fragment[g] == "0":
					if cptG[g-3] == "1":
                                                if g == 3:
                                                        piG -= 4
                                                elif g == 4:
                                                        piG -= 2
                                                elif g == 5:
                                                        piG -= 1
                                elif fragment[g] == "1":
                                        if cptG[g-3] == "0":
                                                if g == 3:
                                                        piG += 4
                                                elif g == 4:
                                                        piG += 2
                                                elif g == 5:
                                                        piG += 1
			for b in range(6,9):
				if fragment[b] == "0":
					if cptB[b-6] == "1":
                                                if b == 6:
                                                        piB -= 4
                                                elif b == 7:
                                                        piB -= 2
                                                elif b == 8:
                                                        piB -= 1
                                elif fragment[b] == "1":
                                        if cptB[b-6] == "0":
                                                if b == 6:
                                                        piB += 4
                                                elif b == 7:
                                                        piB += 2
                                                elif b == 8:
                                                        piB += 1
			pix[c,l] = (piR,piG,piB)
			c += COUNT

	Name = __randName()
        img.save(Name)

        print SUCCESS + "[+] MSG successfully hidden in " + END + Name


############################################
#         Diagonal Insertion in img        #
############################################

def __insertDiag(OBJ,MSG,COLOR,ENC):
	img = __imgOpen(OBJ)
	col, lig = img.size
	pix = img.load()

	try:
		MSG = MSG.encode(ENC)
		print MSG
		bin_msg = __TxtToBin(MSG)
	except:
                if ENC == "base32":
                        MSG = b32encode(MSG)
                        print MSG
                        bin_msg = __TxtToBin(MSG)
                elif ENC == "base16":
                        MSG = b16encode(MSG)
                        print MSG
                        bin_msg = __TxtToBin(MSG)
                else:
                        print MSG
                        bin_msg = __TxtToBin(MSG)

	long = len(bin_msg)
	if long > lig - 2:
		__usage()

	# RED-LSB-DIAG
        # DIAGONAL (TOP LEFT to DOWN RIGHT)
	if COLOR == p_RED:
	        for x in range(long):
	                if bin_msg[x] == "0":
	                        pio = img.getpixel((x,x))
	                        if bin(pio[p_RED])[-1] == '1':
	                                pi = pio[p_RED] - 1
	                                pix[x,x] = (pi,pio[p_GREEN],pio[p_BLUE])
	                elif bin_msg[x] == "1":
	                        pio = img.getpixel((x,x))
	                        if bin(pio[p_RED])[-1] == '0':
	                                pi = pio[p_RED] + 1
	                                pix[x,x] = (pi,pio[p_GREEN],pio[p_BLUE])

	# GREEN-LSB-DIAG
	elif COLOR == p_GREEN:
	        for x in range(long):
	                if bin_msg[x] == "0":
	                        pio = img.getpixel((x,x))
	                        if bin(pio[p_GREEN])[-1] == '1':
	                                pi = pio[p_GREEN] - 1
	                                pix[x,x] = (pio[p_RED],pi,pio[p_BLUE])
	                elif bin_msg[x] == "1":
	                        pio = img.getpixel((x,x))
	                        if bin(pio[p_GREEN])[-1] == '0':
	                                pi = pio[p_GREEN] + 1
	                                pix[x,x] = (pio[p_RED],pi,pio[p_BLUE])

	# BLUE-LSB-DIAG
	elif COLOR == p_BLUE:
		for x in range(long):
			if bin_msg[x] == "0":
				pio = img.getpixel((x,x))
				if bin(pio[p_BLUE])[-1] == '1':
					pi = pio[p_BLUE] - 1
					pix[x,x] = (pio[p_RED],pio[p_GREEN],pi)
			elif bin_msg[x] == "1":
				pio = img.getpixel((x,x))
				if bin(pio[p_BLUE])[-1] == '0':
					pi = pio[p_BLUE] + 1
					pix[x,x] = (pio[p_RED],pio[p_GREEN],pi)

	# Inserts the binary MSG
        # into all Diagonal LSB of IMG_Name
	else:
		c = 0
	        for x in range(0, long, 3):
                        pio = img.getpixel((c,c))
                        piR = pio[p_RED]
                        piG = pio[p_GREEN]
                        piB = pio[p_BLUE]
                        fragment = bin_msg[x:x+3]
                        for i in range(3):
                                if fragment[i] == "0":
       	                                if i == 0:
       	                                        if bin(piR)[-1] == '1':
       	                                                piR -= 1
       	                                elif i == 1:
       	                                        if bin(piG)[-1] == '1':
       	                                                piG -= 1
       	                                elif i == 2:
       	                                        if bin(piB)[-1] == '1':
       	                                                piB -= 1
       	                        elif fragment[i] == "1":
       	                                if i == 0:
       	                                        if bin(piR)[-1] == '0':
       	                                                piR += 1
       	                                elif i == 1:
       	                                        if bin(piG)[-1] == '0':
       	                                                piG += 1
       	                                elif i == 2:
       	                                        if bin(piB)[-1] == '0':
       	                                                piB += 1
                        pix[c,c] = (piR,piG,piB)
			c += 1

	Name = __randName()
        img.save(Name)

	print SUCCESS + "[+] MSG successfully hidden in " + END + Name


######################################
#         Extraction from img        #
######################################

def __extract(OBJ):
	img = __imgOpen(OBJ)
	col,lig = img.size

	#########################################
	#	LSB Diagonal RED extraction	#
	#########################################

	print SUCCESS + "[+] Diagonal " + RED + SUCCESS + " [TOP-LEFT -> BOTTOM-RIGHT] : \n" + END + __Diagonal_LSB(img,lig,p_RED)

	###########################################
        #       LSB Diagonal GREEN extraction     #
        ###########################################

        print SUCCESS + "[+] Diagonal " + GREEN + SUCCESS + " [TOP-LEFT -> BOTTOM-RIGHT] : \n" + END + __Diagonal_LSB(img,lig,p_GREEN)

	##########################################
        #       LSB Diagonal BLUE extraction     #
        ##########################################

        print SUCCESS + "[+] Diagonal " + BLUE + SUCCESS + " [TOP-LEFT -> BOTTOM-RIGHT] : \n" + END + __Diagonal_LSB(img,lig,p_BLUE)

	#########################################
        #       LSB Diagonal RGB extraction     #
        #########################################

	EXT,trEXT = '',''
	for x in range(lig):
                pix = img.getpixel((x,x))
                for i in range(3):
			EXT += bin(pix[i])[-1]
                	if len(EXT) == 8:
                        	trEXT += chr(int('0b' + EXT, 2))
                        	EXT = ''
        print SUCCESS + "[+] Diagonal " + RGB + SUCCESS + " [TOP-LEFT -> BOTTOM-RIGHT] : \n" + END + trEXT

	#################################################
        #       LSB First 3 lines RED extraction 1/1    #
        #################################################

	print SUCCESS + "[+] First 3 lines " + RED + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_RED,-1)

	###################################################
        #       LSB First 3 lines GREEN extraction 1/1    #
        ###################################################

	print SUCCESS + "[+] First 3 lines " + GREEN + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_GREEN,-1)

	##################################################
        #       LSB First 3 lines BLUE extraction 1/1    #
        ##################################################

	print SUCCESS + "[+] First 3 lines " + BLUE + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_BLUE,-1)

	#################################################
        #       LSB First 3 lines RGB extraction 1/1    #
        #################################################

	EXT,trEXT = '',''
        for y in range(3):
                for x in range(col):
			pix = img.getpixel((x,y))
			for i in range(3):
                        	EXT += bin(pix[i])[-1]
                        	if len(EXT) == 8:
                        	        trEXT += chr(int('0b' + EXT, 2))
                                	EXT = ''
        print SUCCESS + "[+] First 3 lines " + RGB + SUCCESS + " [TOP-LEFT] : \n" + END + trEXT

	#################################################
        #       LSB First 3 lines RED extraction 1/2    #
        #################################################

        print SUCCESS + "[+] First 3 lines 1/2 " + RED + SUCCESS + " [TOP-LEFT] : \n" + END + __1on2_LSB(img,col,p_RED)

	###################################################
        #       LSB First 3 lines GREEN extraction 1/2    #
        ###################################################

        print SUCCESS + "[+] First 3 lines 1/2 " + GREEN + SUCCESS + " [TOP-LEFT] : \n" + END + __1on2_LSB(img,col,p_GREEN)

	##################################################
        #       LSB First 3 lines BLUE extraction 1/2    #
        ##################################################

        print SUCCESS + "[+] First 3 lines 1/2 " + BLUE + SUCCESS + " [TOP-LEFT] : \n" + END + __1on2_LSB(img,col,p_BLUE)

	#################################################
        #       LSB First 3 lines RGB extraction 1/2    #
        #################################################

	EXT,trEXT = '',''
        for y in range(3):
	        for x in range(col-1):
                	if x % 2 == 0 or x == 0:
				pix = img.getpixel((x,y))
        		for i in range(3):
                        		EXT += bin(pix[i])[-1]
                                	if len(EXT) == 8:
                                       		trEXT += chr(int('0b' + EXT, 2))
                                       		EXT = ''
        print SUCCESS + "[+] First 3 lines 1/2 " + RGB + SUCCESS + " [TOP-LEFT] : \n" + END + trEXT

	#######################################################
        #       LSB First 3 lines 2 LSB RED extraction 1/1    #
        #######################################################

        print SUCCESS + "[+] First 3 lines 2 LSB " + RED + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_RED,-2)

        #########################################################
        #       LSB First 3 lines 2 LSB GREEN extraction 1/1    #
        #########################################################

        print SUCCESS + "[+] First 3 lines 2 LSB " + GREEN + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_GREEN,-2)

        ########################################################
        #       LSB First 3 lines 2 LSB BLUE extraction 1/1    #
        ########################################################

        print SUCCESS + "[+] First 3 lines 2 LSB " + BLUE + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_LSB(img,col,p_BLUE,-2)

        ##########################################################
        #       LSB First 3 lines 2 LSB of RGB extraction 1/1    #
        ##########################################################

        EXT,trEXT = '',''
        for y in range(3):
                for x in range(col):
                        pix = img.getpixel((x,y))
                        for i in range(3):
                                EXT += bin(pix[i])[-2:]
                                if len(EXT) == 8:
                                        trEXT += chr(int('0b' + EXT, 2))
                                        EXT = ''
        print SUCCESS + "[+] First 3 lines 2 LSB " + RGB + SUCCESS + " [TOP-LEFT] : \n" + END + trEXT

	#######################################################
        #       LSB First 3 lines 3 LSB RED extraction 1/1    #
        #######################################################

        print SUCCESS + "[+] First 3 lines 3 LSB " + RED + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_3_LSB(img,col,p_RED)

        #########################################################
        #       LSB First 3 lines 3 LSB GREEN extraction 1/1    #
        #########################################################

        print SUCCESS + "[+] First 3 lines 3 LSB " + GREEN + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_3_LSB(img,col,p_GREEN)

        ########################################################
        #       LSB First 3 lines 3 LSB BLUE extraction 1/1    #
        ########################################################

        print SUCCESS + "[+] First 3 lines 3 LSB " + BLUE + SUCCESS + " [TOP-LEFT] : \n" + END + __1on1_3_LSB(img,col,p_BLUE)

        #######################################################
        #       LSB First 3 lines 3 LSB RGB extraction 1/1    #
        #######################################################

        EXT,trEXT = '',''
        for y in range(3):
                for x in range(col):
                        pix = img.getpixel((x,y))
                        for i in range(3):
                                EXT += bin(pix[i])[-3:]
                                if len(EXT) > 8:
                                        trEXT += chr(int('0b' + EXT[:8], 2))
                                        EXT = '' + EXT[-len(EXT)+8:]
        print SUCCESS + "[+] First 3 lines 3 LSB " + RGB + SUCCESS + " [TOP-LEFT] : \n" + END + trEXT


#################################
#	  Entry point		#
#################################

if __name__ == "__main__":
	try:
		OPT = sys.argv[1]
		TRG = sys.argv[2]
	except:
		print ERROR + "\nERROR [#0]: Cannot find enough args ... Quitting.\n" + END
		__usage()

	if OPT == "-idr" or OPT == "--insert-diag-red":
		if sys.argv[3] == "-enc":
			try:
				ENC = sys.argv[4]
			except:
				print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
				__usage()
			try:
				MSG = sys.argv[5]
			except:
				print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
				__usage()

			__insertDiag(TRG,MSG,p_RED,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
			__usage()

	elif OPT == "-idg" or OPT == "--insert-diag-green":
		if sys.argv[3] == "-enc":
			try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()

        	        __insertDiag(TRG,MSG,p_GREEN,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-idb" or OPT == "--insert-diag-blue":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()

	                __insertDiag(TRG,MSG,p_BLUE,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-ida" or OPT == "--insert-diag-rgb":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()

        	        __insertDiag(TRG,MSG,p_RGB,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-ir" or OPT == "--insert-red":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
               	 	except:
               	         	print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
               	         	__usage()
                	try:
                        	MSG = sys.argv[5]
                	except:
                	        print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                	        __usage()
			print len(MSG)
                	__insert(TRG,MSG,p_RED,1,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-ig" or OPT == "--insert-green":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()
			print len(MSG)
                	__insert(TRG,MSG,p_GREEN,1,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-ib" or OPT == "--insert-blue":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()
			print len(MSG)
        	        __insert(TRG,MSG,p_BLUE,1,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-ia" or OPT == "--insert-rgb":
		if sys.argv[3]:
                	try:
               		        ENC = sys.argv[4]
                	except:
                	        print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                	        __usage()
                	try:
                	        MSG = sys.argv[5]
                	except:
                	        print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                	        __usage()
			print len(MSG)
                	__insert(TRG,MSG,p_RGB,1,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-i2r" or OPT == "--insert-pair-red":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
       		        except:
       	        	         print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
       	                	 __usage()
			print len(MSG)
                	__insert(TRG,MSG,p_RED,2,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-i2g" or OPT == "--insert-pair-green":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
        	        except:
        	                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
        	                __usage()
        	        try:
        	                MSG = sys.argv[5]
        	        except:
        	                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
        	                __usage()
			print len(MSG)
        	        __insert(TRG,MSG,p_GREEN,2,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-i2b" or OPT == "--insert-pair-blue":
		if sys.argv[3] == "-enc":
	                try:
        	                ENC = sys.argv[4]
               	 	except:
                 	       print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                 	       __usage()
                	try:
                	        MSG = sys.argv[5]
                	except:
                	        print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                	        __usage()
			print len(MSG)
                	__insert(TRG,MSG,p_BLUE,2,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-i2a" or OPT == "--insert-pair-rgb":
		if sys.argv[3] == "-enc":
	                try:
	                        ENC = sys.argv[4]
	                except:
	                        print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
	                        __usage()
	                try:
	                        MSG = sys.argv[5]
	                except:
	                        print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
	                        __usage()
			print len(MSG)
	                __insert(TRG,MSG,p_RGB,2,ENC)
		else:
			print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ir2" or OPT == "--insert-2-bits-red":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_RED,1,ENC,2)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ig2" or OPT == "--insert-2-bits-green":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_GREEN,1,ENC,2)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ib2" or OPT == "--insert-2-bits-blue":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_BLUE,1,ENC,2)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ir3" or OPT == "--insert-3-bits-red":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_RED,1,ENC,3)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ig3" or OPT == "--insert-3-bits-green":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_GREEN,1,ENC,3)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ib3" or OPT == "--insert-3-bits-blue":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_BLUE,1,ENC,3)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

        elif OPT == "-ia3" or OPT == "--insert-3-bits-rgb":
                if sys.argv[3] == "-enc":
                        try:
                                ENC = sys.argv[4]
                        except:
                                print ERROR + "\nERROR [#2]: No encryption selected ... Quitting.\n" + END
                                __usage()
                        try:
                                MSG = sys.argv[5]
                        except:
                                print ERROR + "\nERROR [#4]: No message to insert ... Quitting.\n" + END
                                __usage()
                        print len(MSG)
                        __insert_23_(TRG,MSG,p_RGB,1,ENC,3)
                else:
                        print ERROR + "\nERROR [#3]: No encryption option selected ... Quitting.\n" + END
                        __usage()

	elif OPT == "-e" or OPT == "--extract":
		__extract(TRG)
	else:
		print ERROR + "\nERROR [#1]: No argument " + END + sys.argv[1]  + ERROR + " found ... Quitting.\n" + END
	        __usage()
