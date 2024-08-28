FROM armdocker.seli.gic.ericsson.se/proj-ldc/common_base_os/sles:3.18.0-18
RUN zypper ar -C -G -f https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-ldc-repo-rpm-local/common_base_os/sles/3.18.0-18 LDC-CBO-SLES \
 && zypper ref -f -r LDC-CBO-SLES \
 && zypper install -y python3 glibc-locale \
 && zypper clean --all \
# Remove hundreds of megabytes of unused locales, until the following Jira is resolved which should allow us to do this with a package ADPPRG-20627
 && mv /usr/lib/locale/C.utf8 /C.utf8 \
 && rm -rf /usr/lib/locale/* \
 && mv /C.utf8 /usr/lib/locale/

# A locale needs to be installed and set for later use by some python packages like click
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN zypper install -y python3-pip ca-certificates-mozilla

RUN mkdir -p /usr/src/app/custom_exporter
WORKDIR /usr/src/app/custom_exporter

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY exporter.py .

EXPOSE 8080

ENTRYPOINT ["python3", "./exporter.py"]
