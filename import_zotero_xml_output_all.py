# Purpose:
# This python code will read in a Zotero bibliography file saved in xml format,
# identify studies with brain coordinates associated with resiliency or susceptibility
# to specific psychiatric disorder (MDD, PTSD, SZ, bipolar)
# and save coordinates as composite Sleuth/GingerALE compliant text file
#
# Note, also creating separate Sleuth/GingerALE compliant text files for each disorder
# for comparison in GingerALE
#
# Update March 2 2024:  My goal was to revise code to loop through each factor (resiliency vs. susceptibility) and disorder,
# but some elements must be hard-coded.
# So creating this composite file to generate both serially.
# This file will also create dictionaries of exclusion and inclusion criteria.
#
# Update September 4 2024:  Manuscript submitted last week. For the manuscript, I renamed the Zotero bibliography as:
#       Resilience_Systematic_Review.xml
# Filename was updated below and changes pushed to github.
#
# Copyright Andrew James PhD, 5-2-2024

## Initializing

# initialize code to read XML
import urllib.request, urllib.parse, urllib.error
import xml.etree.ElementTree as ET
import ssl
import sys
from bs4 import BeautifulSoup
#import lxml
import os
dir_workspace = 'A:\\People\\Andy James\\projects\\R01 Resiliency\\metaanalysis data\\workspace\\'
dir_data = 'A:\\People\\Andy James\\projects\\R01 Resiliency\\metaanalysis data\\7 first pass and gray search combined\\'

# go to workspace directory
os.chdir(dir_workspace)

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# declare XML file to read and Sleuth/GingerALE text output
#  note, hardcoded
xml_filename = dir_data + 'Resilience_Systematic_Review.xml' # library was renamed for mansucript submission to be more specific;  filename updated here 9/4/2024
roifile_res = './rois_resilience.txt'
roifile_res_MDD = './rois_resilience_MDD.txt'
roifile_res_PTSD = './rois_resilience_PTSD.txt'
roifile_res_SZ = './rois_resilience_SZ.txt'
roifile_res_BD = './rois_resilience_BD.txt'
roifile_sus = './rois_susceptibility.txt'
roifile_sus_MDD = './rois_susceptibility_MDD.txt'
roifile_sus_PTSD = './rois_susceptibility_PTSD.txt'
roifile_sus_SZ = './rois_susceptibility_SZ.txt'
roifile_sus_BD = './rois_susceptibility_BD.txt'
# declare empty strings for Major Depressive Disorder (MDD), PTSD, Schizophrenia (SZ) and Bipolar disorder (BD)
str_res = ''
str_res_MDD = ''
str_res_PTSD = ''
str_res_SZ = ''
str_res_BD = ''
str_sus = ''
str_sus_MDD = ''
str_sus_PTSD = ''
str_sus_SZ = ''
str_sus_BD = ''
# counter for included articles that are excluded because coords not in MNI or TT space (e.g. Freesurfer atlases)
count_exclude_nonMNIorTT_res = 0
count_exclude_nonMNIorTT_sus = 0


# sample code to read xml with beautiful soup
#content = []
#with open(xml_filename, 'r') as file:
#    # Read each line in the file, readlines() returns a list of lines
#    content = file.readlines()
#    # Combine the lines in the list into a string
#    content = "".join(content)
#    bs_content = BeautifulSoup(content, "lxml")

# note: code below is useful if Zotero exports space as &amp;nbsp;
#type(bs_content)
#bs_content_pretty = bs_content.prettify()
#type(bs_content_pretty)
#bs_content_pretty.replace('&amp;nbsp;',' ') # this is removing other spaces too!
# example:  N=349ample normativebsp; &amp;nbsp;-21 &amp;nbsp; &amp;nbsp;6 &amp;nbsp; &amp;nbsp;-27


# use ElementTree to easily traverse xml tree
# if reading from a file....

tree = ET.parse(xml_filename)
root = tree.getroot()

#with open(xml_filename, 'r') as f:
#    tree = ET.fromstring(f.read())
#root = tree.getroot()

# and let's create a dictionary of disorders in database
dict_disorders_res = {}
dict_disorders_sus = {}

# if reading from string parsed by BeautifulSoup...
#root = ET.fromstring(bs_content)

## First, generate text files for ROIs promoting resilience:
with open(roifile_res, 'w', encoding='utf-16') as f:
    for allrecords in root.findall('records'):
        for thisrecord in allrecords.findall('record'):
            # extract relevant information about article
            # extract year
            thisdate = thisrecord.findall('dates')
            thisyear = thisdate[0][0].text
            #print(thisyear)

            # extract first author surname
            thiscontributors = thisrecord.findall('contributors')
            if len(thiscontributors) == 0:
                thisauthor_full = 'BLANK'
            else:
                thisauthor_full = thiscontributors[0][0][0].text
            thisauthor_split = thisauthor_full.split(',')
            thisauthor_lastname = thisauthor_split[0]
            #print(thisauthor_lastname)

            # initialize sample size to 0;   will replace with N=xxx in research-notes  later
            N=0
            research_notes = thisrecord.findall('research-notes') # research_notes behaves like a string
            for temp in research_notes:
                line = str(temp.text)

                for entry in line.split('\r\r'):
                    if entry.startswith("n=") or entry.startswith("N="):
                        entry_split=entry.split('=')
                        N = entry_split[1]

            # Now, search for "3rd resilienc*" or "4th resilienc*" in "research-notes" field
            research_notes = thisrecord.findall('research-notes') # redundant, but keeping
            # let's create dummy flags indicating is coordinates are associated with MDD/depression, PTSD, SZ/schizophrenia
            MDD = 0
            PTSD = 0
            SZ = 0
            BD = 0

            str_to_write = '' # empty string that will be filled with meta-data and written to file as appropriate

            for temp in research_notes:
                print_flag = 0
                # print flag will create block of Sleuth/GingerALE readable text if it finds "4th resilienc*
                # First line will be commented text with year, author, journal, sample size (?)
                # Followed by coordinates
                line = str(temp.text)
                for entry in line.split('\r\r'):
                    entry = entry.replace('&nbsp;',' ') # sometimes Zotero web-version replaces spaces with &nbsp;
                    # identify associated disorder, if any
                    # first, add to dictionary of disorders

                    if 'diseas' in entry: # extract relevant disorder
                        #print(entry)
                        disorder_str = entry.split(' ')
                        #print(disorder_str)
                        disorder_str = disorder_str[2]
                        #print(disorder_str)

                    # next, specifically flag MDD, PTSD, Schizophrenia, BD
                    if any(word in entry for word in ['MDD','depres']):
                        MDD = 1
                    elif 'PTSD' in entry:
                        PTSD = 1
                    elif 'schizo' in entry:
                        SZ = 1
                    elif 'bipolar' in entry:
                        BD = 1

                    if entry.startswith("4th res") or entry.startswith("3rd res"): # if entry includes MNI or TT coordinates, then prompts writing of data
                        #print(thisyear + ' ' + thisauthor_lastname + ' ')
                        #print(entry) # spot-check:  print output and check for non MNI/TT coordinates
                        if entry.find(' MNI') > 0:
                            print_flag = 1
                            str_to_write = str('\n') + '// Reference=MNI ' + str('\n')
                        elif entry.find(' TT') > 0:
                            print_flag = 1
                            str_to_write = str('\n') + '// Reference=Talairach ' +  str('\n')
                        else:
                            # Note: Some articles met inclusion criteria but did not report coordinates in MNI or TT - for example, reported freesurfer regions or reported using Destrieux atlas
                            # need to separately flag these for exclusion
                            # Manually count N=7 articles excluded for this reason (resiliency)
                            print_flag = 0
                            count_exclude_nonMNIorTT_res += 1

                        if print_flag == 1:  # writing relevant meta-data about study
                            #str_to_write = str_to_write + entry + str('\n')  # spot-check... confirming resiliency is being written
                            str_to_write = str_to_write + '// ' + str(thisauthor_lastname) + ' ' + str(thisyear) + str('\n') + '// Subjects=' + str(N) + str('\n')
                        continue # the next lines in entry are coordinates; so we are leaving print_flag "on" and writing these coordinates.  Code below will "turn off" writing by setting print flag to 0
                        # this is why I have to serialize, since some studies have both resiliency and susceptibility coordinates

                    elif entry.startswith('4th note'):
                        print_flag = 0
                    elif entry.startswith('4th susc') or entry.startswith('3rd susc'):
                        print_flag = 0
                    elif entry.startswith("Acces"):
                        print_flag = 0
                    elif entry.startswith("N"):
                        print_flag = 0
                    elif entry.startswith("n"):
                        print_flag=0
                    elif entry.startswith("4th sample") or entry.startswith("3rd sample"):
                        print_flag = 0

                    if print_flag == 1: # if print_flag is still 1, then there are one or more lines of coordinates to write
                        entry_split = entry.split()
                        str_to_write = str_to_write + str(entry_split[1]) + ' ' + str(entry_split[2]) + ' ' +  str(entry_split[3]) + str('\n')

                if len(str_to_write) > 0: # i.e. not empty
                    #print(thisyear)
                    #print(thisauthor_lastname)
                    #print(str_to_write)
                    f.write(str_to_write)

                    # Also add disorder to disease dictionary
                    if disorder_str not in dict_disorders_res.keys():
                        dict_disorders_res[disorder_str] = 0
                    dict_disorders_res[disorder_str] += 1

                    # and if MDD, PTSD, SZ or BD, write to separate file
                    if MDD == 1:
                        str_res_MDD = str_res_MDD + str_to_write
                    elif PTSD == 1:
                        str_res_PTSD = str_res_PTSD + str_to_write
                    elif SZ == 1:
                        str_res_SZ = str_res_SZ + str_to_write
                    elif BD == 1:
                        str_res_BD = str_res_BD + str_to_write
f.close()

# Now print MDD, PTSD, and SZ specific resilience files
#   Note: I know there must be a more elegant way.
#   But this works
f = open(roifile_res_MDD, 'w', encoding='utf-16')
f.write(str_res_MDD)
f.close()

f = open(roifile_res_PTSD, 'w', encoding='utf-16')
f.write(str_res_PTSD)
f.close()

f = open(roifile_res_SZ, 'w', encoding='utf-16')
f.write(str_res_SZ)
f.close()

f = open(roifile_res_BD, 'w', encoding='utf-16')
f.write(str_res_BD)
f.close()

## Repeat for susceptibility

## First, generate text files for ROIs promoting susceptibility:
with open(roifile_sus, 'w', encoding='utf-16') as f:
    for allrecords in root.findall('records'):
        for thisrecord in allrecords.findall('record'):
            # extract relevant information about article
            # extract year
            thisdate = thisrecord.findall('dates')
            thisyear = thisdate[0][0].text
            #print(thisyear)

            # extract first author surname
            thiscontributors = thisrecord.findall('contributors')
            if len(thiscontributors) == 0:
                thisauthor_full = 'BLANK'
            else:
                thisauthor_full = thiscontributors[0][0][0].text
            thisauthor_split = thisauthor_full.split(',')
            thisauthor_lastname = thisauthor_split[0]
            #print(thisauthor_lastname)

            # initialize sample size to 0;   will replace with N=xxx in research-notes  later
            N=0
            research_notes = thisrecord.findall('research-notes') # research_notes behaves like a string
            for temp in research_notes:
                line = str(temp.text)

                for entry in line.split('\r\r'):
                    if entry.startswith("n=") or entry.startswith("N="):
                        entry_split=entry.split('=')
                        N = entry_split[1]

            # Now, search for susceptibility in "research-notes" field
            research_notes = thisrecord.findall('research-notes') # redundant, but keeping
            # let's create dummy flags indicating is coordinates are associated with MDD/depression, PTSD, SZ/schizophrenia
            MDD = 0
            PTSD = 0
            SZ = 0
            BD = 0

            str_to_write = '' # empty string that will be filled with meta-data and written to file as appropriate

            for temp in research_notes:
                print_flag = 0
                # print flag will create block of Sleuth/GingerALE readable text if it finds "4th susc*
                # First line will be commented text with year, author, journal, sample size (?)
                # Followed by coordinates
                line = str(temp.text)
                for entry in line.split('\r\r'):
                    entry = entry.replace('&nbsp;',' ') # sometimes Zotero web-version replaces spaces with &nbsp;
                    # identify associated disorder, if any
                    # first, add to dictionary of disorders

                    if 'diseas' in entry: # extract relevant disorder
                        #print(entry)
                        disorder_str = entry.split(' ')
                        #print(disorder_str)
                        disorder_str = disorder_str[2]
                        #print(disorder_str)

                    # next, specifically flag MDD, PTSD, Schizophrenia, BD
                    if any(word in entry for word in ['MDD','depres']):
                        MDD = 1
                    elif 'PTSD' in entry:
                        PTSD = 1
                    elif 'schizo' in entry:
                        SZ = 1
                    elif 'bipolar' in entry:
                        BD = 1

                    if entry.startswith("4th sus") or entry.startswith("3rd sus"): # if entry includes MNI or TT coordinates, then prompts writing of data
                        #print(thisyear + ' ' + thisauthor_lastname + ' ')
                        #print(entry) # spot-check:  print output and check for non MNI/TT coordinates (e.g. Freesurfer)
                        if entry.find(' MNI') > 0:
                            print_flag = 1
                            str_to_write = str('\n') + '// Reference=MNI ' + str('\n')
                        elif entry.find(' TT') > 0:
                            print_flag = 1
                            str_to_write = str('\n') + '// Reference=Talairach ' +  str('\n')
                        else:
                            print_flag = 0
                            # Count 5 articles that meet inclusion criteria but did not report results in MNI or TT (e.g. Freesurfer)
                            count_exclude_nonMNIorTT_sus += 1

                        if print_flag == 1:  # writing relevant meta-data about study
                            #str_to_write = str_to_write + entry + str('\n')  # spot-check... confirming susceptibility is being written
                            str_to_write = str_to_write + '// ' + str(thisauthor_lastname) + ' ' + str(thisyear) + str('\n') + '// Subjects=' + str(N) + str('\n')
                        continue # the next lines in entry are coordinates; so we are leaving print_flag "on" and writing these coordinates.  Code below will "turn off" writing by setting print flag to 0
                        # this is why I have to serialize, since some studies have both resiliency and susceptibility coordinates

                    elif entry.startswith('4th note'):
                        print_flag = 0
                    elif entry.startswith('4th res') or entry.startswith('3rd res'):
                        print_flag = 0
                    elif entry.startswith("Acces"):
                        print_flag = 0
                    elif entry.startswith("N"):
                        print_flag = 0
                    elif entry.startswith("n"):
                        print_flag=0
                    elif entry.startswith("4th sample") or entry.startswith("3rd sample"):
                        print_flag = 0

                    if print_flag == 1: # if print_flag is still 1, then there are one or more lines of coordinates to write
                        entry_split = entry.split()
                        str_to_write = str_to_write + str(entry_split[1]) + ' ' + str(entry_split[2]) + ' ' +  str(entry_split[3]) + str('\n')

                if len(str_to_write) > 0: # i.e. not empty
                    #print(thisyear)
                    #print(thisauthor_lastname)
                    #print(str_to_write)
                    f.write(str_to_write)

                    # Also add disorder to disease dictionary
                    if disorder_str not in dict_disorders_sus.keys():
                        dict_disorders_sus[disorder_str] = 0
                    dict_disorders_sus[disorder_str] += 1

                    # and if MDD, PTSD, SZ or BD, add to string now, and later write to separate file
                    if MDD == 1:
                        str_sus_MDD = str_sus_MDD + str_to_write
                    elif PTSD == 1:
                        str_sus_PTSD = str_sus_PTSD + str_to_write
                    elif SZ == 1:
                        str_sus_SZ = str_sus_SZ + str_to_write
                    elif BD == 1:
                        str_sus_BD = str_sus_BD + str_to_write
f.close()

# Now print MDD, PTSD, and SZ specific susceptibility files
#   Note: I know there must be a more elegant way.
#   But this works
f = open(roifile_sus_MDD, 'w', encoding='utf-16')
f.write(str_sus_MDD)
f.close()

f = open(roifile_sus_PTSD, 'w', encoding='utf-16')
f.write(str_sus_PTSD)
f.close()

f = open(roifile_sus_SZ, 'w', encoding='utf-16')
f.write(str_sus_SZ)
f.close()

f = open(roifile_sus_BD, 'w', encoding='utf-16')
f.write(str_sus_BD)
f.close()


# Finally, use dictionaries to generate list of all reasons for excluding articles
# Note: could integrate this into one (and just one) of code sets above,
# but best to keep separate, so that the two above clode blocks are symmetric (i.e. only differ in res vs sus)
# Further note:  each article is either included or excluded, independent of having resilience or susceptibility coordinates
dict_title = {} # a dictionary for the title of each article, to check for repeats
dict_empty = {} # a dictionary for articles with empty notes field - these have been missed and need to be checked
title_list = [] # as above, but a list
empty_list = [] # as above, but a list
dict_inclusion = {} # dictionary of article titles for all included articles
dict_exclusion = {} # dictionary of article titles for all excluded articles
dict_inclusion_exclusion = {} # a dictionary of all inclusion or exclusion criteria for each article




for allrecords in root.findall('records'):
    for thisrecord in allrecords.findall('record'):
        # extract relevant information about article
        # extract year
        thisdate = thisrecord.findall('dates')
        thisyear = thisdate[0][0].text
        if thisyear is None:
            thisyear='NoYear'
        #print(thisyear)

        # extract title
        thistitle = thisrecord.findall('titles')[0][0].text
        if thistitle is None:
            thistitle = 'No title'

        # extract first author surname
        thiscontributors = thisrecord.findall('contributors')
        if len(thiscontributors) == 0:
            thisauthor_full = 'BLANK'
        else:
            thisauthor_full = thiscontributors[0][0][0].text
        thisauthor_split = thisauthor_full.split(',')
        thisauthor_lastname = thisauthor_split[0]
        #print(thisauthor_lastname)

        nameyeartitle = thisauthor_lastname + '\t' + thisyear + '\t' + thistitle
        if nameyeartitle not in dict_title.keys():
            dict_title[nameyeartitle] = 0
        dict_title[nameyeartitle] += 1

        research_notes = thisrecord.findall('research-notes') # research_notes behaves like a string
        if len(research_notes) == 0: # empty article, investigate
            if nameyeartitle not in dict_empty.keys():
                dict_empty[nameyeartitle] = 0
            dict_title[nameyeartitle] += 1

        flag_inclusion = 0 # article was included in final metaanalysis
        flag_exclusion = 0 # article was excluded from final metaanalysis

        for temp in research_notes:
            line = str(temp.text)
            for entry in line.split('\r\r'):
                entry = entry.replace('&nbsp;',' ') # sometimes Zotero web-version replaces spaces with &nbsp;

                if entry.startswith('4th res') or entry.startswith('3rd res') or entry.startswith('4th sus') or entry.startswith('3rd sus') :
                    # add article to inclusion dictionary
                    if nameyeartitle not in dict_inclusion.keys():
                        dict_inclusion[nameyeartitle] = 0
                    dict_inclusion[nameyeartitle] += 1

                    # add reason for inclusion to inclusion dictionary
                    if entry not in dict_inclusion_exclusion.keys():
                        dict_inclusion_exclusion[entry] = 0
                    dict_inclusion_exclusion[entry] += 1

                    flag_inclusion = 1

                elif 'exc' in entry:  # else if contains word exclude...
                    # add article to exclusion dictionary
                    if 'keep' not in entry:  # adjust for occasional note '1st keep (but maybe exclude later)'
                        # add article to exclusion dictionary
                        if nameyeartitle not in dict_exclusion.keys():
                            dict_exclusion[nameyeartitle] = 0
                        dict_exclusion[nameyeartitle] += 1

                        if entry not in dict_inclusion_exclusion.keys():
                            dict_inclusion_exclusion[entry] = 0
                        dict_inclusion_exclusion[entry] += 1

                        flag_exclusion = 1

        if flag_exclusion == 0 and flag_inclusion == 0:
            print('This article was neither included nor excluded:  ' + nameyeartitle)

## Above code has created dictionary of reasons for inclusion or exclusion
# Next step:  generate report of reasons for excluding articles

# print all inclusion and exclusion criteria from dictionary, for visualization purposes
# Also save these to a tsv file for supplemental materials in manuscript
file_inclusion_exclusion = './dictionary_inclusion_exclusion.tsv'
with open(file_inclusion_exclusion,'w') as f:
    print('Reason for Inclusion or Exclusion in Meta-analysis\tNumber of Articles\n')
    f.write('Reason for Inclusion or Exclusion in Meta-analysis\tNumber of Articles\n')
    for key, value in dict_inclusion_exclusion.items():
        print(key + '\t' + str(value))
        f.write(key + '\t' + str(value) + '\n')
f.close()

# Disclaimer:  needed guidance from ChatGPT for this solution.
# creating a definition to make this easier
def find_exclusion_criteria(this_string, this_dict):
    exclusion_sum = 0
    for key, value in this_dict.items():
        if any(this_string in key for this_string in this_string):
            exclusion_sum += int(value)
    print("Total sum of exclusion criteria containing search terms [{}]: {}".format(" or ".join(this_string), exclusion_sum))

# sample
find_exclusion_criteria(['sample', 'nonhuman', 'case study'], dict_inclusion_exclusion)
# no neuroimaging
find_exclusion_criteria(['neuroimaging','exclude behavioral only'], dict_inclusion_exclusion)
# definition of resilience:  i.e. a resilient algorithm or resiliency against traumatic brain injury or postsurgical outcomes
find_exclusion_criteria(['exclude def'], dict_inclusion_exclusion)
# exclude because studies cognitive reserve in natural aging - technically a subtype of definition of resilience, but sufficient numbers to warrant its own criteria
find_exclusion_criteria(['cognitive reserve'], dict_inclusion_exclusion)
# exclude because review - note, this also includes 1st pass reviews, so subtract 40 when reporting
find_exclusion_criteria(['exclude review'], dict_inclusion_exclusion)
# exclude because no data: i.e. an abstract from conference proceeding, or a theoretical "white paper"
find_exclusion_criteria(['exclude no data','white paper','no resiliency measure'], dict_inclusion_exclusion)
# exclude no coordinates provided
find_exclusion_criteria(['exclude no coord','poor source localization'], dict_inclusion_exclusion)
# behind a paywall that I cannot access - excluding out of respect to Open Science
find_exclusion_criteria(['paywall'], dict_inclusion_exclusion)


# note, some articles provided ROIs from Desikan-Killany or Destrieux atlases. This is a gray area:
# technically, these articles meet inclusion for the meta-analyses
# However, the articles do not provide coordinates.
# It could be possible to calculate a center of mass for use as coordinates, but that involves speculation beyond scope of original article.
# For this manuscript, for purposes of creating table of inclusion and exclusion process, we are counting these as exclusions due to "n ocoordinates"
print('\n')
print('Total number of articles with exclusion criteria: ' + str(len(dict_exclusion)))
print('Total number of articles with inclusion criteria: ' + str(len(dict_inclusion)))
print('Note: the number of articles meeting inclusion criteria includes articles reporting results in atlases other than MNI or TT space (ex: Destrieux atlas).')
print('To generate table of results, subtract this number from "included articles" and add to "excluded no coordinates"')
find_exclusion_criteria(['Destrieux','Desikan-Killany','freesurfer'], dict_inclusion_exclusion)

## Conversion issues
# Text files were written in utf-16 due to a formatting issue.  But Sleuth and GingerALE are having trouble reading.
# Solution is to read each roifile back in as utf-16 and save as utf-8

for thisfile in [roifile_res,roifile_res_BD,roifile_res_MDD,roifile_res_PTSD,roifile_res_SZ,roifile_sus,roifile_sus_BD,roifile_sus_MDD,roifile_sus_PTSD,roifile_sus_SZ]:
    with open(thisfile, 'r', encoding='utf-16') as f:
        TEMP = f.read()
    f.close()

    with open(thisfile, 'w', encoding='utf-8') as f:
        f.write(TEMP)
    f.close()

## Contrast analyses
# In order to compare activations predicting resilience in one disorder vs. another, have to generate a pooled text file of coordinates
# Next generate ALE on pooled sample
# Then gingerALE will compare pooled sample ALE vs. individual sample ALE
#
# Logic:  for 4 disorders, iteratively open and combine text file of coordinates

disorders = ['PTSD','SZ','MDD','BD']
for i in range(len(disorders)):
    dis1 = disorders[i]
    for j in range(i+1,len(disorders)):
        dis2 = disorders[j]
        file1 = eval('roifile_res_' +dis1)
        file2 = eval('roifile_res_' + dis2)
        fileout = './rois_resilience_combined_' + dis1 + '_' + dis2 + '.txt'
        with open(file1, 'r', encoding='utf-8') as f1:
            coords1 = f1.read()
        with open(file2, 'r', encoding='utf-8') as f2:
            coords2 = f2.read()
        # note: confirmed that each file ends in a line break, so can just concatenate
        coords3 = coords1 + coords2
        with open(fileout, 'w', encoding='utf-8') as f3:
            f3.write(coords3)


# and repeat for susceptibility
for i in range(len(disorders)):
    dis1 = disorders[i]
    for j in range(i+1,len(disorders)):
        dis2 = disorders[j]
        file1 = eval('roifile_sus_' +dis1)
        file2 = eval('roifile_sus_' + dis2)
        fileout = './rois_susceptibility_combined_' + dis1 + '_' + dis2 + '.txt'
        with open(file1, 'r', encoding='utf-8') as f1:
            coords1 = f1.read()
        with open(file2, 'r', encoding='utf-8') as f2:
            coords2 = f2.read()
        # note: confirmed that each file ends in a line break, so can just concatenate
        coords3 = coords1 + coords2
        with open(fileout, 'w', encoding='utf-8') as f3:
            f3.write(coords3)
