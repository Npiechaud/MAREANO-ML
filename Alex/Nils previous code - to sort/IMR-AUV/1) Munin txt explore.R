library(tidyverse)
library(magrittr)


# IMR laptop
"C:/Users/a40754/OneDrive - Havforskningsinstituttet" -> base

WD <- paste0(base,"/IMR AUV")
setwd(WD)
# a dir containing the headers of each files
headers_dir <- paste0(WD,"/munin headers")

# set dive directory 
DiveDir <- "C:/Users/a40754/Documents/AUV images/Mission_55_20220601_4"
DiveDir <- "C:/Users/a40754/Documents/AUV images/Mission_55_20220606_2" 


# open all the headers
paste0(headers_dir,"/format.txt") %>% read_delim()


fileName <-paste0(headers_dir,"/format.txt")
conn <- file(fileName,open="r")
linn <-readLines(conn)

# all the txt files names 
tibble( line = 1:length(linn), info = linn) %>%
  mutate(is_file = linn %>%  str_detect(pattern = ".txt")) %>% 
# remove the
  mutate(filename =  str_remove(info, pattern = 'Format of file \"') %>% 
           str_remove(pattern = '\"')) -> diveheaders

# list all files that are in the dive folder 
DiveDir %>% list.files(pattern = "*.txt", recursive = T) %>% 
  tibble(file = .) %>% 
  mutate(filename = basename(file), path = dirname(file)  ) -> divefiles

# what line number for nav pos? 
headers_meta <- diveheaders %>% filter(is_file == TRUE) %>% mutate(start = "", end = "")

# attach file names 
headers_meta %<>% left_join(divefiles, by = "filename")

I = 12 # for NAV position
I = 7 # for depth.txt that has altitude

files_headers <- list()
for (I in 1:nrow(headers_meta)) {
  

# select the txt file to process
txtfile <- "navpos.txt"
txtfile <- headers_meta %>%  slice(I) %>% pull(filename)

print(txtfile)
# extract start line
diveheaders %>% filter(is_file == T) %>% filter(filename == txtfile) -> d.1 
n1 <- d.1$line
# extract last line 
diveheaders %>% filter(is_file == T) %>% mutate(line2 = 1:nrow(.)) -> d2
n2 <- d2 %>% slice(d2 %>% filter(filename == txtfile) %>% pull(line2 )+1 ) %>% pull(line) -1 

# extract all relevant line for that txt file
diveheaders %>% slice(n1:n2) -> d.i
# update headers meta
headers_meta %<>% mutate(start = ifelse(filename==txtfile,n1,start), 
                        end = ifelse(filename==txtfile,n2,end) )  

# parse names so that we can find the headers of each file
d.i %>% 
  select(info) %>% 
  mutate(info2 = 
  str_replace(info, pattern = "   ",replacement = "")  ) %>% 
  separate(info2, sep = ": ",into = c("index","column")) %>% 
  mutate(index =  gsub("[^0-9.-]", "", index) )  %>% 
  # take the second part of the column names
  mutate(column =  sub(".* ", "" , info  ))  -> dnames.i

## !!!! DEAL WITH DUPLICATED NAMES !!!! 

# add some metadata 
dnames.i %<>%  
  mutate(file = txtfile)


files_headers[[I]] <- dnames.i
names(files_headers)[I] <- txtfile

# open the actual data
headers_meta %>% filter(filename == txtfile) %>% 
pull(file) %>% paste0(DiveDir,"/", .) %>% 
  read_delim(.,
             delim = "\t", escape_double = FALSE, 
             col_names = FALSE, trim_ws = TRUE) -> data

# remove first and last names in list of column names 
dnames.i$column[-1] %>% head(-1) -> names(data)

}

# 


# for the navpos table: 
data %>%
  select(Time, NAV_LATITUDE,NAV_LONGITUDE, NAV_DEPTH) %>% 
  # make a date_time column
  mutate(date_time = lubridate::as_datetime(lubridate::as_datetime(Time )) ) -> internalnav

internalnav %>% head()
internalnav %>% tail()



# for the depth and altitude
data %>% 
  # take second column (altitude 1)
  select(Time, contains("ALT_ALTITUDE")) %>% 
  mutate(date_time = lubridate::as_datetime(lubridate::as_datetime(Time )) ) -> internal_altitude
  



# export it

data_for_stitch <- left_join(internalnav, internal_altitude, by = c("Time", "date_time"))
  
data_for_stitch %>% 
  write_csv("internal_nav.csv")








