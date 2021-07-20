#!/bin/bash
# MODIFY:[54,55,56] line

usage (){
    echo -en "Usage: $0 -d<deploy mode> -t<test mode> -g<git source> "\
        "-b<build image> -z<zip image> -P<pull image> -p<push image> "\
        " -e <export image path> -i <import image path> -l<show log> "\
        "-s<run shell smb> -h<help>\n" 1>&2
    echo -en "For example:\n"
    echo -en "1.build zip and push image\n"
    echo -en "  $0 -b -z -p\n\n"
    echo -en "2.run docker debug mode\n"
    echo -en "  $0 -t\n\n"
    echo -en "3.run docker product mode\n"
    echo -en "  $0 -d\n\n"
    exit ${STATE_WARNING}
}


zip_image (){
    echo "zip image"

    if [ $(docker-squash -h | wc -l) -lt 2 ];then
        apt-get install -y python python-pip
        pip install docker-squash
    fi

    if [ $(docker-squash -h | wc -l) -gt 2 ];then
        docker-squash -t $BASE_IMAGE $BASE_IMAGE
    fi
}

while getopts dtgbzPpe:i:lhs: opt
do
    case "$opt" in
    d) DEPLOY=1;;
    t) TEST=1;;
    g) GIT=1;;
    b) BUILD=1;;
    P) PULL=1;;
    p) PUSH=1;;
    z) ZIP=1;;
    e) EXPORT=$OPTARG;;
    i) IMPORT=1;;
    l) LOG=1;;
    s) SERVICE=$OPTARG;;
    h) usage;;
    *) usage;;
    esac
done

export PROJECT_NAME=eii
export BASE_NAME=eii_api
export BASE_VERSION=v1
export BASE_PATH=/root/eii_api
export BASE_IMAGE=docker.dlyunzhi.cn:7114/${PROJECT_NAME}/${BASE_NAME}:${BASE_VERSION}
export LOGPATH=/var/log/${BASE_NAME}/${BASE_VERSION}
export DB_PATH=/data/mysql
export BASE_PORT=7551
export DB_PORT=7552
export WORKERS=2

COMPOSE_FILE=${BASE_PATH}/docker/docker-compose.yml

# run web shell
if [ "${SERVICE}" ];then
    if [ "${SERVICE}" = "gateone" ];then
        echo "run service ${SERVICE}"

        if [ "$(docker ps | grep 0.0.0.0:10443)" ];then
            CONTAINER=$(docker ps | grep 0.0.0.0:10443 | awk '{print $1}')
            echo -n "docker kill "
            docker kill $CONTAINER
            sleep 1
        fi

        docker run --rm -d -p 10443:10443 -p 8000:8000 docker.dlyunzhi.cn:7114/common/gateone python /gateone/GateOne/run_gateone.py
    fi


    if [ "${SERVICE}" = "samba" ];then
        echo "run service ${SERVICE}"

        if [ "$(docker ps | grep 0.0.0.0:139)" ];then
            CONTAINER=$(docker ps | grep 0.0.0.0:139 | awk '{print $1}')
            echo -n "docker kill "
            docker kill $CONTAINER
            sleep 1
        fi

        docker run --rm -it -p 139:139 -p 445:445 -v /root/deploy:/share -d docker.dlyunzhi.cn:7114/common/samba -p -s "share;/share;yes;no;yes;"
    fi

    if [ "${SERVICE}" = "backup" ];then
        echo "run service ${SERVICE}"
        # create cron job
        if [ -z "`crontab -l | grep "install.sh -s backup"`" ];then
            crontab -l > tempcron
            echo "0 */4 * * * /bin/sh ${BASE_PATH}/install.sh -s backup" >> tempcron
            crontab tempcron
            rm tempcron
        fi

        BACKUP_PATH=$DB_PATH/backup/${BASE_NAME}
        BACKUP_FILENAME=${BASE_NAME}_DB_`date +%Y%m%d`.tar.gz

        mkdir -p $BACKUP_PATH

        # compress bak file
        cd $DB_PATH
        tar zcf $BACKUP_PATH/${BACKUP_FILENAME} ${BASE_NAME}

        # delete before 30 days created backup file
        find ${BACKUP_PATH} -mtime +31 -name "*.tar.gz" -exec rm {} \;
    fi

    exit 0
fi

# show log
if [ "${LOG}" ];then
    tail -f "${LOGPATH}/app.log" "${LOGPATH}/gunicorn_error.log"
    exit 0
fi

# get git source
if [ "${GIT}" ];then
    BRANCH=origin/develop

    RET=`git fetch --all 2>&1 | wc -l`
    if [ ${RET} -eq 1 ];then
        # no source update
        exit 0
    fi
    git reset --hard ${BRANCH}
    git pull
    chmod 777 install.sh
fi

# pull image from registry
if [ "${PULL}" ];then
    echo "pull ${BASE_IMAGE} image from registry"
    docker pull ${BASE_IMAGE}
fi

# build image
if [ "${BUILD}" ];then
    echo "build image ${BASE_IMAGE}"
    docker build --build-arg BASE_NAME=${BASE_NAME} -t ${BASE_IMAGE} \
    -f ${BASE_PATH}/docker/Dockerfile .
fi

if [ "${ZIP}" ]; then
    zip_image
fi

# push image to registry
if [ "${PUSH}" ];then
    echo "push ${BASE_IMAGE} image to registry"
    docker push ${BASE_IMAGE}
fi

# export image to compress file
if [ "${EXPORT}" ];then
    FILE_NAME=${BASE_NAME}_${BASE_VERSION}

    echo "export product image(${BASE_IMAGE}) to ${EXPORT}/${FILE_NAME}.tar.gz"
    docker save ${BASE_IMAGE} > ${FILE_NAME}.tar
    tar zcvf ${FILE_NAME}.tar.gz ${FILE_NAME}.tar

    echo "copy deploy file into ${EXPORT}"
    mkdir -p ${EXPORT}/docker
    cp install.sh ${EXPORT}/
    cp README.md ${EXPORT}/
    cp docker/docker-compose.yml ${EXPORT}/docker/
    mv ${FILE_NAME}.tar.gz ${EXPORT}/
    rm -rf ${FILE_NAME}.tar
fi

# import image from compress file
if [ "${IMPORT}" ];then
    FILE_NAME=${BASE_NAME}_${BASE_VERSION}

    echo "import product image(${BASE_IMAGE}) from ${FILE_NAME}.tar.gz"
    tar zxvf ${FILE_NAME}.tar.gz
    docker load < ${FILE_NAME}.tar
    rm -rf ${FILE_NAME}.tar
fi

# run the application
if [ "${DEPLOY}" ]; then
    echo "deploy the application"
    /usr/local/bin/docker-compose -f ${COMPOSE_FILE} down
    /usr/local/bin/docker-compose -f ${COMPOSE_FILE} up -d
elif [ "${TEST}" ]; then
    echo "run the application"
    # use develop source
    if [ -d "${BASE_PATH}/project" ];then
        TESTARG="-v ${BASE_PATH}:/opt/${BASE_NAME}"
    fi

    if [ "$(docker ps | grep 0.0.0.0:${BASE_PORT})" ];then
        CONTAINER=$(docker ps | grep 0.0.0.0:${BASE_PORT} | awk '{print $1}')
        echo -n "docker kill "
        docker kill $CONTAINER
        sleep 1
    fi

    /usr/local/bin/docker-compose -f ${COMPOSE_FILE} run ${TESTARG} \
    --rm --no-deps --service-ports api /bin/bash
fi

echo "exit shell"
