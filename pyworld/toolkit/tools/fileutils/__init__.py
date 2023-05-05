try:
    from .krate.fileutils import save, load,files_with_extention,file_datetime,filter,dirs,files
except:
    import traceback
    print("Failed to find krate: install from:")
    print("git@github.com:BenedictWilkinsAI/krate.git")
    traceback.print_exc()
