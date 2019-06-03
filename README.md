# DiffCover
一种简单的差异代码覆盖实验代码

## basev2是基于tomcat的简单servlet应用
#### 基于jacoco获取代码覆盖。请先阅读相关文档。
#### 修改catalina.sh 
#### JAVA_OPTS="$JAVA_OPTS -javaagent:/Users/pingan/workspace/jacoco-0.8.3/lib/jacocoagent.jar=includes=*,output=tcpserver,port=9527,address=127.0.0.1,append=true -Xverify:none"
#### 进入basev2项目，运行ant report 获取全量代码覆盖


## basediff.py获取差异代码覆盖


