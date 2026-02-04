from setuptools import setup,find_packages
from typing import List

def get_requirements(file_path: str)->List[str]:
    '''
    this function will returen the list of requirments
    given the file path

    '''
    requiremetnts = []
    with open(file_path) as file_obj:
        requiremetnts = file_obj.readlines()
        requiremetnts = [req.replace('\n',"") for req in requiremetnts]

    if '-e .' in requiremetnts:
        requiremetnts.remove('-e .')

    return requiremetnts
setup(
    name='job-recommendation-system',
    version='0.0.1',
    author='Zakaria',
    author_email='zakariahmed870@gmail.com',
    packages = find_packages(),
    install_requires = get_requirements('requirements.txt')
)