from setuptools import setup, find_packages


install_requires = [
    'sentry>=8.10.0',
]

tests_require = [
]

setup(
    name='sentry-auth-saml2',
    version='0.1',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='https://github.com/ojii/sentry-auth-saml2',
    description='SAML2 authentication provider for Sentry',
    license='BSD',
    packages=find_packages(exclude=['tests', 'project']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'tests': tests_require},
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'auth_saml2 = sentry_auth_saml2',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
