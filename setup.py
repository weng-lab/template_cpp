#!/usr/bin/env python

# by purcaro@gmail.com

import subprocess, sys, os, argparse, re
from collections import namedtuple
import getpass, socket
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '../metadata/utils'))
from utils import Utils

BuildPaths = namedtuple("BuildPaths", 'url build_dir build_sub_dir local_dir')

def shellquote(s):
    # from http://stackoverflow.com/a/35857
    return "'" + s.replace("'", "'\\''") + "'"

def isMac():
    return sys.platform == "darwin"

class Paths():
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "external"))
        self.ext_tars = os.path.join(self.base_dir, "tarballs")
        self.ext_build = os.path.join(self.base_dir, "build")
        self.install_dir = os.path.join(self.base_dir, "local")
        Utils.mkdir_p(self.ext_tars)
        Utils.mkdir_p(self.ext_build)
        self.paths = {}
        self.paths["R-devel"] = self.__Rdevel()
        self.paths["armadillo"] = self.__armadillo()
        self.paths["bamtools"] = self.__bamtools()
        self.paths["jsoncpp"] = self.__jsoncpp()
        self.paths["boost"] = self.__boost()
        self.paths["cppcms"] = self.__cppcms()
        self.paths["cppitertools"] = self.__cppitertools()
        self.paths["dlib"] = self.__dlib()
        self.paths["liblinear"] = self.__liblinear()
        self.paths["mathgl"] = self.__mathgl()
        self.paths["mlpack"] = self.__mlpack()
        self.paths["zi_lib"] = self.__zi_lib()
        self.paths["svmlin"] = self.__svmlin()

    def path(self, name):
        if name in self.paths:
            return self.paths[name]
        raise Exception(name + " not found in paths")

    def __zi_lib(self):
        url = 'git@github.com:weng-lab/zi_lib.git'
        local_dir = os.path.join(self.install_dir, "zi_lib")
        return BuildPaths(url, '', '', local_dir)

    def __bamtools(self):
        url = 'git@github.com:pezmaster31/bamtools.git'
        name = "bamtools"
        build_dir = os.path.join(self.ext_build, name)
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        fn = os.path.basename(url)
        fn_noex = fn.replace(".git", "")
        build_sub_dir = os.path.join(build_dir, fn_noex)
        local_dir = os.path.join(self.install_dir, name)
        return BuildPaths(url, build_dir, build_sub_dir, local_dir)

    def __jsoncpp(self):
        url = "https://github.com/open-source-parsers/jsoncpp/archive/1.7.4.tar.gz"
        return self.__package_dirs(url, "jsoncpp", addPrefix = True)

    def __cppitertools(self):
        url = 'git@github.com:ryanhaining/cppitertools.git'
        local_dir = os.path.join(self.install_dir, "cppitertools")
        return BuildPaths(url, '', '', local_dir)

    def __Rdevel(self):
        url = "http://cran.cnr.berkeley.edu/src/base/R-3/R-3.2.2.tar.gz"
        return self.__package_dirs(url, "R-devel")

    def __boost(self):
        url = "http://downloads.sourceforge.net/project/boost/boost/1.61.0/boost_1_61_0.tar.gz"
        return self.__package_dirs(url, "boost")

    def __armadillo(self):
        url = "http://iweb.dl.sourceforge.net/project/arma/armadillo-6.500.5.tar.gz"
        url = "http://pilotfiber.dl.sourceforge.net/project/arma/armadillo-7.300.1.tar.xz"
        return self.__package_dirs(url, "armadillo")

    def __mlpack(self):
        url = "http://www.mlpack.org/files/mlpack-1.0.8.tar.gz"
        return self.__package_dirs(url, "mlpack")

    def __liblinear(self):
        url = "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/multicore-liblinear/liblinear-multicore-2.11-1.zip"
        return self.__package_dirs(url, "liblinear")

    def __cppcms(self):
        url = "http://freefr.dl.sourceforge.net/project/cppcms/cppcms/1.0.5/cppcms-1.0.5.tar.bz2"
        return self.__package_dirs(url, "cppcms")

    def __mathgl(self):
        url = "http://freefr.dl.sourceforge.net/project/mathgl/mathgl/mathgl%202.2.2/mathgl-2.2.2.1.tar.gz"
        return self.__package_dirs(url, "mathgl")

    def __dlib(self):
        url = "http://freefr.dl.sourceforge.net/project/dclib/dlib/v18.7/dlib-18.7.tar.bz2"
        return self.__package_dirs(url, "dlib")

    def __svmlin(self):
        url = "http://vikas.sindhwani.org/svmlin-v1.0.tar.gz"
        return self.__package_dirs(url, "svmlin")

    def __package_dirs(self, url, name, addPrefix = False):
        build_dir = os.path.join(self.ext_build, name)
        fn = os.path.basename(url)
        fn_noex = fn.replace(".tar.gz", "").replace(".tar.bz2", "").replace(".zip", "").replace(".tar.xz", "")
        if addPrefix:
            fn_noex = name + '-' + fn_noex
        build_sub_dir = os.path.join(build_dir, fn_noex)
        local_dir = os.path.join(self.install_dir, name)
        return BuildPaths(url, build_dir, build_sub_dir, local_dir)

class Setup:
    def __init__(self, args):
        self.paths = Paths()
        self.args = args
        self.__processArgs()

    def __processArgs(self):
        dirs = self.args.dirsToDelete
        if not dirs:
            return

        if "all" == dirs[0]:
            dirs = []
            for k, _ in self.paths.paths.iteritems():
                dirs.append(k)

        for e in dirs:
            p = self.__path(e)
            if p.build_dir:
                Utils.rm_rf(p.build_dir)
            if p.local_dir:
                Utils.rm_rf(p.local_dir)

    def __path(self, name):
        return self.paths.path(name)

    def __setup(self, name, builder_f):
        if os.path.exists(self.__path(name).local_dir):
            print name, "found"
        else:
            print name, "NOT found; building..."
            builder_f()

    def setup(self):
        self.__setup("zi_lib", self.zi_lib)
        self.__setup("cppitertools", self.cppitertools)
        self.__setup("jsoncpp", self.jsoncpp)
        self.__setup("liblinear", self.liblinear)
        #self.__setup("bamtools", self.bamtools)
        self.__setup("armadillo", self.armadillo)
        #self.__setup("cppcms", self.cppcms)
        self.__setup("boost", self.boost)
        #self.__setup("dlib", self.dlib)
        #self.__setup("svmlin", self.svmlin)
        #self.__setup("mathgl", self.mathgl)
        #self.__setup("R-devel", self.Rdevel)
        #self.__setup("mlpack", self.mlpack)

    def on_cluster(self):
        host = socket.gethostname()
        if host in ["ghpcc06", "ghpcc-sgi"]:
            return True
        if re.match(r"c\d\db\d\d\Z", host, re.DOTALL):
            return True
        return False

    def num_cores(self):
        if self.on_cluster():
            return 1
        c = Utils.num_cores()
        if c > 8:
            return c/2
        if 1 == c:
            return 1
        return c - 1

    def __build(self, i, cmd):
        print "\t getting file..."
        fnp = Utils.get_file_if_size_diff(i.url, self.paths.ext_tars)
        Utils.clear_dir(i.build_dir)
        Utils.untar(fnp, i.build_dir)
        try:
            Utils.run_in_dir(cmd, i.build_sub_dir)
        except:
            print("running:", cmd)
            sys.exit(1)

    def boost(self):
        print("boost requires bzip2 libraries, else it will fail during compilation...")
        i = self.__path("boost")
        if isMac():
          cmd = """echo "using darwin : 3.2 : /usr/local/bin/g++-3.2 ;  " >> tools/build/v2/user-config.jam && ./bootstrap.sh --prefix={local_dir} && ./b2 -d 2 toolset=darwin-4.9 -j {num_cores} install && install_name_tool -change libboost_system.dylib {local_dir}/lib/libboost_system.dylib {local_dir}/lib/libboost_thread.dylib && install_name_tool -change libboost_system.dylib {local_dir}/lib/libboost_system.dylib {local_dir}/lib/libboost_filesystem.dylib""".format(local_dir=shellquote(i.local_dir).replace(' ', '\ '), num_cores=self.num_cores())
          #cmd = """echo "using gcc : 4.9 : /usr/local/bin/g++-4.9 ; " >> tools/build/v2/user-config.jam &&
          # ./bootstrap.sh --prefix={local_dir} && ./bjam --toolset=gcc-4.9 -j {num_cores} install
          #  """.format(
          #             local_dir=shellquote(i.local_dir).replace(' ', '\ '), num_cores=self.num_cores())
        else:
          cmd = """./bootstrap.sh --prefix={local_dir} --with-libraries=date_time,filesystem,iostreams,math,regex,serialization,system,program_options,log && ./b2 -d 2 -j {num_cores} install""".format(local_dir=shellquote(i.local_dir).replace(' ', '\ '), num_cores=self.num_cores())
        print cmd
        self.__build(i, cmd)

    def Rdevel(self):
        i = self.__path("R-devel")
        cmd = ""
        if isMac():
          cmd = """
            ./configure --prefix={local_dir} --enable-R-shlib CC=gcc-4.9 CXX=g++-4.9
            && make -j {num_cores}
            && make install
            && echo 'install.packages(c(\"ape\", \"ggplot2\", \"seqinr\",\"Rcpp\", \"RInside\"), repos=\"http://cran.us.r-project.org\")' | $({local_dir}/R.framework/Resources/bin/R RHOME)/bin/R --slave --vanilla
            """.format(local_dir=shellquote(i.local_dir).replace(' ', '\ '), num_cores=self.num_cores())
        else:
          cmd = """
          unset CPP && unset CXX && unset CC &&
            ./configure --prefix={local_dir} --enable-R-shlib
            && make -j {num_cores}
            && make install
            && echo 'install.packages(c(\"ape\", \"ggplot2\", \"seqinr\",\"Rcpp\", \"RInside\"), repos=\"http://cran.us.r-project.org\")' | $({local_dir}/lib/R/bin/R RHOME)/bin/R --slave --vanilla
            """.format(local_dir=shellquote(i.local_dir).replace(' ', '\ '), num_cores=self.num_cores())

        cmd = " ".join(cmd.split())
        self.__build(i, cmd)

    def bamtools(self):
        i = self.__path('bamtools')
        cmd = "git clone {url} {d}".format(url=i.url, d=i.build_dir)
        Utils.run(cmd)
        i = self.__path('bamtools')
        cmd = "mkdir -p build && cd build && CC=gcc-4.9 CXX=g++-4.9 cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} .. && make -j {num_cores} install".format(
            local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        Utils.run_in_dir(cmd, i.build_dir)

    def jsoncpp(self):
        i = self.__path('jsoncpp')
        cmd = "mkdir -p build && cd build && CC=gcc CXX=g++ cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} .. && make -j {num_cores} install".format(
            local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        self.__build(i, cmd)

    def cppcms(self):
        i = self.__path('cppcms')
        if(sys.platform == "darwin"):
            cmd = "mkdir -p build && cd build && CC=gcc-4.9 CXX=g++-4.9 cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} .. && make -j {num_cores} install && install_name_tool -change libbooster.0.dylib {local_dir}/lib/libbooster.0.dylib {local_dir}/lib/libcppcms.1.dylib".format(local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        else:
            cmd = "mkdir -p build && cd build && CC=gcc-4.9 CXX=g++-4.9 cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} .. && make -j {num_cores} install ".format(local_dir=shellquote(i.local_dir), num_cores=self.num_cores())

        self.__build(i, cmd)

    def armadillo(self):
        i = self.__path('armadillo')
        cmd = "mkdir -p build && cd build && cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} .. && make -j {num_cores} install".format(
            local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        self.__build(i, cmd)

    def liblinear(self):
        i = self.__path('liblinear')
        # patch -p1 -i ../../../liblinear-2.1.2-patch.diff &&
        cmd = """
make &&
mkdir -p {local_dir} &&
cp predict train {local_dir} &&
make lib &&
cp linear.h liblinear.so.3 README {local_dir} &&
ln -s {local_dir}/liblinear.so.3 {local_dir}/liblinear.so
""".format(local_dir=shellquote(i.local_dir))
        cmd = " ".join(cmd.split("\n"))
        self.__build(i, cmd)

    def mlpack(self):
        i = self.__path('mlpack')
        armadillo_dir = shellquote(i.local_dir).replace("mlpack", "armadillo")
        boost_dir = shellquote(i.local_dir).replace("mlpack", "boost")
        # from http://stackoverflow.com/a/17049807
        cmd = """
mkdir -p build
&& cd build
&& CC=gcc-4.9 CXX=g++-4.9 cmake -D DEBUG=OFF -D PROFILE=OFF
        -DBoost_NO_BOOST_CMAKE=TRUE
        -DBoost_NO_SYSTEM_PATHS=TRUE
        -DBOOST_ROOT:PATHNAME={BOOST_DIR}
        -DBoost_LIBRARY_DIRS:FILEPATH={BOOST_DIR}/lib
        -DARMA_64BIT_WORD=TRUE
        -DARMADILLO_LIBRARY={armadillo_dir}/lib/libarmadillo.so.4.300.2
        -DARMADILLO_INCLUDE_DIR={armadillo_dir}/include/
        -DCMAKE_INSTALL_PREFIX:PATH={local_dir} ..
&& make -j {num_cores} install
""".format(local_dir=shellquote(i.local_dir), armadillo_dir=armadillo_dir, num_cores=self.num_cores(), BOOST_DIR=boost_dir)
        cmd = " ".join(cmd.split('\n'))
        self.__build(i, cmd)

    def mathgl(self):
        i = self.__path('mathgl')
        cmd = """
mkdir -p build &&
cd build &&
CC=gcc-4.9 CXX=g++-4.9 cmake -DCMAKE_INSTALL_PREFIX:PATH={local_dir} -Denable-qt5=on .. &&
make -j {num_cores} install
""".format(local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        cmd = " ".join(cmd.split('\n'))
        self.__build(i, cmd)

    def dlib(self):
        i = self.__path('dlib')
        cmd = """
mkdir {local_dir} &&
cp -a * {local_dir}/
""".format(local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        cmd = " ".join(cmd.split('\n'))
        self.__build(i, cmd)

    def svmlin(self):
        i = self.__path('svmlin')
        cmd = """
mkdir {local_dir} &&
cp -a * {local_dir}/
""".format(local_dir=shellquote(i.local_dir), num_cores=self.num_cores())
        cmd = " ".join(cmd.split('\n'))
        self.__build(i, cmd)

    def __git(self, i):
        cmd = "git clone {url} {d}".format(url=i.url, d=shellquote(i.local_dir))
        Utils.run(cmd)

    def zi_lib(self):
        self.__git(self.__path('zi_lib'))

    def cppitertools(self):
        self.__git(self.__path('cppitertools'))

    def ubuntu(self):
        pkgs = """libbz2-dev python2.7-dev cmake libpcre3-dev zlib1g-dev libgcrypt11-dev libicu-dev
python doxygen doxygen-gui auctex xindy graphviz libcurl4-openssl-dev""".split()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirsToDelete', type=str, nargs='*')
    return parser.parse_args()

def main():
    args = parse_args()
    s = Setup(args)
    s.setup()
main()
