import os
import boto3
from botocore.exceptions import ClientError
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# importing custom modules
import ec2_aws
import s3_aws


# Constants
MAIN_MENU = """ ====== Services ======
[ 1 ] EC2
[ 2 ] S3
[ 3 ] Cloudwatch
[ 0 ] Quit
"""
main_menu_list = [1,2,3,0]

EC2_MENU = """ ====== EC2 services ====== 
[ 1 ] List Available Regions
[ 2 ] Listing Instances
[ 3 ] Create KeyPair
[ 4 ] Create Security-Group
[ 5 ] Manage Instance (create, monitor, stop, terminate)
[ 0 ] Back
"""
ec2_menu_list = [1,2,3,4,5,0]

EC2_INSTANCE = """ ====== Manage Instance ======
[ 1 ] Status of Intance
[ 2 ] Create Instance
[ 3 ] Start Instance
[ 4 ] Stop Instacne
[ 5 ] Terminate Instance
[ 0 ] Back
"""
ec2_instance_list = [1,2,3,4,5,0]

CLOUDWATCH_MENU = """ ====== Metrics ======
[ 1 ] CPU Utilization
[ 2 ] Incoming Network Packets
[ 3 ] Outgoing Network Packets
[ 4 ] CPU Credit Usage
[ 5 ] CPU Credit Balance
[ 0 ] Back
"""
cloudwatch_menu_list = [1,2,3,4,5,0]

# Cloudwatch available metrics dict
metrics_dict = {1:"CPUUtilization", 2:"NetworkPacketsIn", 3:"NetworkPacketsOut", 4:"CPUCreditUsage", 5:"CPUCreditBalance"}

S3_MENU = """ ====== S3 services ======
[ 1 ] List Available Regions
[ 2 ] List All Buckets
[ 3 ] Create Bucket
[ 4 ] Empty Bucket
[ 5 ] Upload File to Bucket
[ 6 ] Download File from Bucket
[ 7 ] Delete File in Bucket
[ 8 ] Delete Bucket
[ 0 ] Back
"""
s3_menu_list = [1,2,3,4,5,6,7,8,0]

# menu dictionary to show options
MENU_DICT = {1:MAIN_MENU, 2:EC2_MENU, 3:EC2_INSTANCE, 4:CLOUDWATCH_MENU, 5:S3_MENU, 0:""}
# menu list to choose options
menu_list_dict = {1:main_menu_list, 2:ec2_menu_list, 3:ec2_instance_list, 4:cloudwatch_menu_list,   5:s3_menu_list}


# Printing the requested menu
def print_menu(index=0, clear=False, menu=True):
    if clear:
        os.system("cls")
    if menu:
        print("\n"+MENU_DICT[index])
    #return list(MENU_DICT[index])


# Getting the input from user
def get_input(choice_list):
    check = False
    while not check:
        try:
            choice = int(input("Input: "))
            if not (choice in choice_list):
                raise Exception
            return choice
        except:
            print(" Invalid input, try again!")
            pass


# get string input
def get_str_input():
    print("Allowed format: lower case, only letters")

    while True:
        try:
            text = input("Input: ")
            if text.islower() and text.isalpha():
                return text
            else:
                print("Invalid input")
        except:
            print("Invalid input")
            pass


# main menu loop function
def main_menu_loop(ec2_client, ec2_resoure, s3_client, s3_resource, cloudwatch):
    global menu_list_dict
    index = 1
    print_menu(clear=True, menu=False)

    while True:
        print_menu(index, clear=True)
        choice = get_input(menu_list_dict[index])
        if choice == 1:
            ec2_menu_loop(ec2_client, ec2_resoure)

        elif choice == 2:
            s3_menu_loop(s3_client, s3_resource, ec2_client)

        elif choice == 3:
            cloudwatch_loop(cloudwatch)

        else:
            print_menu(clear=True, menu=False)
            return
            

# EC2 menu loop function
def ec2_menu_loop(ec2_client, ec2_resource):
    global menu_list_dict
    index = 2
    print_menu(clear=True, menu=False)

    while True:
        print_menu(index)
        choice = get_input(menu_list_dict[index])
        if choice == 1:
            ec2_aws.list_regions(ec2_client)

        elif choice == 2:
            ec2_aws.get_running_instances(ec2_resource)

        elif choice == 3:
            try:
                print("Enter a KeyPair name")
                key_name = get_str_input()
                ec2_aws.create_key_pair(ec2_client, key_name)
                print("KeyPair created successfully. File name:", key_name + ".pem")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 4:
            try:
                print("Enter a SecurityGroup name")
                security_group_name = get_str_input()
                ec2_aws.create_sec_group(ec2_client, security_group_name)
                print("Security Group created successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 5:
            ec2_instance_loop(ec2_client, ec2_resource)

        else:
            print_menu(clear=True, menu=False)
            return


# EC2 instance loop function
def ec2_instance_loop(ec2_client, ec2_resource):
    global menu_list_dict
    index = 3
    print_menu(clear=True, menu=False)

    while True:
        print_menu(index)
        choice = get_input(menu_list_dict[index])
        if choice == 1:
            try:
                id_instance = input("Please enter instance ID: ")
                ec2_aws.status_instance(ec2_resource, id_instance)
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 2:
            try:
                # getting all the arguments from user input
                region_name = input("Please enter region code: ")
                keyname = input("Enter KeyPair name: ")
                security_group_id = input("Enter Security Group ID: ")
                print("How many instances do you want to launch")
                maxcount = get_input([1,2,3])
                imageID = "ami-0bd9c26722573e69b"  # Ubuntu Server 20.04 LTS (64bit x86)
                instancetype = "t3.micro"
                mincount = maxcount

                # calling instance creation function
                ec2_client = boto3.client("ec2", region_name=region_name)
                ec2_aws.create_instance(ec2_client, imageID, mincount, maxcount, instancetype, keyname, security_group_id)
                print("Instance(s) created successfully")

            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 3:
            try:
                id_instance = input("Please enter instance ID: ")
                ec2_aws.start_stop_instance(ec2_client, id_instance, True)
                print("Instance started successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 4:
            try:
                id_instance = input("Please enter instance ID: ")
                ec2_aws.start_stop_instance(ec2_client, id_instance, False)
                print("Instance stopped successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 5:
            try:
                id_instance = input("Please enter instance ID: ")
                ec2_aws.terminate_instance(ec2_client, id_instance)
                print("Instance terminated successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        else:
            print_menu(clear=True, menu=False)
            return


# cloudwatch loop function
def cloudwatch_loop(cloudwatch):
    global menu_list_dict
    index = 4
    print_menu(clear=True, menu=False)

    while True:
        print_menu(index)
        choice = get_input(menu_list_dict[index])
        
        if choice == 0:
            print_menu(clear=True, menu=False)
            return

        try:
            id_instance = input("Please enter instance ID: ")
            get_metrics_image(cloudwatch, id_instance, metrics_dict[choice])
        except Exception as e:
            print("Problem occured:", e)
            pass


# S3 menu loop function
def s3_menu_loop(s3_client, s3_resource, ec2_client):
    global menu_list_dict
    index = 5
    print_menu(clear=True, menu=False)

    while True:
        print_menu(index)
        choice = get_input(menu_list_dict[index])
        if choice == 1:
            ec2_aws.list_regions(ec2_client)
            
        elif choice == 2:
            # Later add an option to select a region
            s3_aws.print_content(s3_client)

        elif choice == 3:
            try:
                # Later add an option to select a region
                print("Enter a name for bucket")
                bucket_name = get_str_input()
                s3_aws.create_bucket(s3_resource, bucket_name)
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 4:
            try:
                print("Enter a name for bucket")
                bucket_name = input("Input: ")
                s3_aws.empty_bucket(s3_resource, bucket_name)
                print("Bucket emptied successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 5:
            try:
                bucket_name = input("Please enter bucketname: ")
                file_name = input("Please enter filename: ")
                s3_aws.upload_file(s3_resource, bucket_name, "files/"+file_name, file_name)
                print("File uploaded successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass
        
        elif choice == 6:
            try:
                bucket_name = input("Please enter bucketname: ")
                file_name = input("Please enter filename: ")
                s3_aws.download_file(s3_client, bucket_name, file_name)
                print("File downloaded successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 7:
            try:
                bucket_name = input("Please enter bucketname: ")
                file_name = input("Please enter filename: ")
                s3_aws.delete_file(s3_resource, bucket_name, file_name)
                print("File deleted successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        elif choice == 8:
            try:
                bucket_name = input("Please enter bucketname: ")
                s3_aws.delete_bucket(s3_client, bucket_name)
                print("Bucket deleted successfully")
            except Exception as e:
                print("Problem occured:", e)
                pass

        else:
            print_menu(clear=True, menu=False)
            return


# Showing the metrics (Cloudwatch)
def get_metrics_image(cloudwatch, instance_id, metric_name):
    try:
        json = '{"metrics": [["AWS/EC2", "' + metric_name +'", "InstanceId", "'+ instance_id +'"]]}'
        response = cloudwatch.get_metric_widget_image(MetricWidget=json)

        file_name = "charts/chart-" + instance_id +'-'+ metric_name + ".png"
        with open (file_name, 'wb') as f:
            f.write(response["MetricWidgetImage"])
        
        plt.title(metric_name)
        plt.imshow(mpimg.imread(file_name))
        plt.show()
    except Exception as e:
        print("Invalid input, please try again!")
        print(e)
        pass


# =============== Program starts here ===========================
if __name__ == "__main__":

    # Regions = {Stockholm: eu-north-1, Frankfurt: eu-central-1}
    region = "eu-north-1"

    # creating the clients
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    ec2_client = boto3.client("ec2", region_name=region)
    ec2_resoure = boto3.resource("ec2", region_name=region)
    cloudwatch = boto3.client("cloudwatch", region_name=region)
 
    # calling the main function
    main_menu_loop(ec2_client, ec2_resoure, s3_client, s3_resource, cloudwatch)
    print("Program finished")
# ================================================================
