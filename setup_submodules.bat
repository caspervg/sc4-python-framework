@echo off
echo Setting up git submodules for SC4 Python Framework...

git submodule add https://github.com/nsgomez/gzcom-dll.git vendor/gzcom-dll
git submodule add https://github.com/pybind/pybind11.git vendor/pybind11

git submodule update --init --recursive

echo Submodules setup complete!
pause