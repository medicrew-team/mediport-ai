# 패키지 업데이트 및 git, ssh, vim 설치
apt update && apt install -y git openssh-server vim

# SSH 설정 파일 수정 (PermitRootLogin / PubkeyAuthentication)
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^#\?PubkeyAuthentication .*/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# root 비밀번호 설정 - 수동 입력을 유도
echo "root 계정 비밀번호:"
passwd

# SSH 서버 재시작
service ssh restart

echo "서버 초기화 완료됨."