import os

class FileClear:
    def clear(dir, name, file_type, index=None):
        if index != None:
            os.remove(os.path.join(dir, f'{name}_{index}.{file_type}'))
            return
        
        index = 0
        while os.path.exists(os.path.join(dir, f'{name}_{index}.{file_type}')):
            os.remove(os.path.join(dir, f'{name}_{index}.{file_type}'))
            index += 1