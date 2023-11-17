
#Nils why create another variable here? why not just use local_images_dir in code below?

# 1) Create table       ----------------------------------------------------------------------------
images_dir <- local_images_dir 

# make a table of images and path to each of them
images_dir %>%  list.files(recursive = T, full.names = T) -> imgs_paths
images_dir %>%  list.files(recursive = T,
                           full.names = F,
                           include.dirs = F) -> imgs_list
imgs_list %>%  str_split(pattern = "/") %>%
  map(~ extract2(.x, length(.x))) %>%
  unlist() -> imgs_names

#Nils do you plan to put folder "ALL_IMAGES" ON github? Just wondering if we really need multiple columns for variations of image file paths. Why not just have full path and image name separate. 

# format the table
tibble(image = imgs_list,
       path = imgs_paths,
       filename = imgs_names) -> img_PATHWAYS


# 2) Add the pathways to the images ----------------------------------------------------------------------------

# merge it with the the image metadata including the path and dimensions
  img_PATHWAYS %>%  left_join(All_labels, . , by = "filename" ) %>% distinct(image_label_id, .keep_all = T) -> All_labels_path

# make sure all images are matched to their pathways
All_labels_path %>% filter(is.na(path)) -> mismatched # 


if(nrow(mismatched) == 0){
  print_color(color = "green", text = "All images have been found - proceed")
}else{
  print_color(color = "red", text = paste0("Warning: ", nrow(mismatched %>% distinct(filename)), " image(s) have not been matched (out of ", nrow(img_PATHWAYS %>% distinct(filename) ),") \n\n"))

  print_color(color = "red", text = paste0("Mismatched images are: ", mismatched %>%  distinct(filename) %>% pull ))

}

# if you want to know what the mismatches are, call the mismatched table in the console