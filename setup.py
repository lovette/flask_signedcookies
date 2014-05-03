from setuptools import setup

setup(
    name='flask_signedcookies',
    version='1.0.0',
    url='https://github.com/lovette/flask_signedcookies',
	download_url = 'https://github.com/lovette/flask_signedcookies/archive/master.tar.gz',
    license='BSD',
    author='Lance Lovette',
    author_email='lance.lovette@gmail.com',
    description='Flask extension that provides easy access to signed cookies.',
    long_description=open('README.md').read(),
    py_modules=['flask_signedcookies',],
    install_requires=['Flask',],
    tests_require=['nose',],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
