read -p "REMOVE? OLD MODEL AND DOWNLOAD THE NEWEST ONE FROM HUGGINGFACE? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
rm base.pt extra.pt
clear
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/base.pt
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/extra.pt
clear
echo "DONE."