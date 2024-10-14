import subprocess

def compile_qrc():
    qrc_file = 'Images.qrc'
    output_file = 'CompiledImages.py'
    try:
        subprocess.run(['pyrcc5', qrc_file, '-o', output_file], check=True)
        print(f"Compiled {qrc_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile {qrc_file}: {e}")