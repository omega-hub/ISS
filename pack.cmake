pack_module_dir()

if(WIN32)
    file(WRITE ${PACKAGE_DIR}/ISS.bat 
        "./bin/orun.exe -D %~dp0% ISS/iss.py")
endif()
