import os

from setuptools import find_packages, setup

import router_api


def read(fname):
    # file read function copied from sorl.django-documents project
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


install_requires = [
    'requests',
]

setup(
    name='pyrouter',
    version=router_api.__version__,
    description="TPlink api, currently only support TL-R470GP model",
    long_description_content_type="text/x-rst",
    long_description=read('README.md'),
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='tplink API TLR470GP',
    author='Dong Zhuang',
    author_email='dzhuang.scut@gmail.com',
    url='https://github.com/dzhuang/pyrouter/',
    license='MIT',
    packages=find_packages("pyrouter"),
    include_package_data=True,
    zip_safe=True,
    install_requires=install_requires,
    entry_points="""
        # -*- Entry points: -*-
    """,
)
