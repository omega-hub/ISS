request_dependency(cyclops)
request_dependency(omegaOsgEarth)

install(DIRECTORY . DESTINATION omegalib/ISS PATTERN ".git" EXCLUDE)
