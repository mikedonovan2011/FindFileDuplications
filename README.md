# FindFileDuplications
Finds files (i.e. pics) that are duplicate but might have different filenames and might be in totally different places in the folders you specify.

You can specify a number of folders as your inputs. All files in all folders and sub-folders are analyzed. If the file of a particular (configured) type, it is hashed.

If the hash hasn't been seen yet, a file is created in a "non-dupes" folder with:
    a) filename of <hash>.txt, 
    b) the path/file of the file that was hashed as the contents of the file.
        
If the file with the hash already exists in the non-dupes folder, the file is appended 
with the path/file that was hashed. It is then moved to the dupes folder.

If the file with the hash already exists in the dupes folder, the file is appended. 

Checking for these conditions happens in the reverse order as described above.