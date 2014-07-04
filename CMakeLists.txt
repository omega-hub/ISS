request_dependency(cyclops)
request_dependency(omegaOsgEarth)

# Download and extract ISS data 
if(NOT EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/data)
	message(STATUS "Downloading ISS data...")
    file(DOWNLOAD http://omegalib.s3-website-us-west-2.amazonaws.com/ISS/data.tar.gz ${CMAKE_CURRENT_SOURCE_DIR}/data.tar.gz SHOW_PROGRESS)
    execute_process(COMMAND ${CMAKE_COMMAND} -E tar xzf data.tar.gz WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
endif()


install(DIRECTORY . DESTINATION omegalib/ISS PATTERN ".git" EXCLUDE)
