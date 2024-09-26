import os
import shutil
import subprocess

def main():
    # Path to .ipython database
    db_path = os.path.join(
        os.environ['IPYTHONDIR'],
        'profile_default',
        'db'
    )
    print('Path to ipython database: {db_path}')

    # Zip up .ipython database
    print('Zipping variable db...')
    shutil.make_archive('db', 'zip', db_path)
    print('Done.')

    # Upload .ipython database to releases
    subprocess.run([
        'gh', 'release', 'upload', 'data-release',
        'db.zip',
        '--repo', 'cu-esiil-edu/esiil-learning-portal',
        '--clobber'
    ])

    # Delete archive
    print('Deleting archive...')
    os.remove('db.zip')
    print('Done.')
    return

if __name__ == "__main__":
    main()