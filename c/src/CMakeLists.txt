##########################################
##              libepoc                ###
##########################################

# Create a library called "libepoc"
ADD_LIBRARY (emokit STATIC emokit.c) 
target_link_libraries (emokit ${LIBS}) 

INSTALL (TARGETS emokit
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  )

INSTALL(FILES
  ${LIBEMOKIT_HEADERS}
  DESTINATION include/libemokit
  )
