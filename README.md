# preprocessing_reddit

This repository elucidates the way Reddit comment datasets from 2019-2022 were cleaned and preprocessed. 
First, files in '.zst' format were converted to '.txt' format with the 1_zst2text.py file. Please feel free to adjust the karma limit or the age of posters as you see fit, if you decide to use the script. 

Second, file 2_cleaning.py does some basic decluttering along with english language detecting. Again, feel free to adapt. 
Third, 3_cropper.sh is adaptable through arguments specifying directory names and importantly, what chunk from the '.txt' file do you want to crop to create your own train/validation pairs. 

Fourth, 4_train_validation_split.sh will shuffle the newly created files, extract 250,000 lines for the validation file (again, adjustable) and the rest for the test.py file. 

If using SLURM, amend necessary macros. Most of the bash files work with 48 files corresponding to months from 2019 till 2022. If not, feel free to delete them.
