import streamlit as st
from Home import face_rec
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av

st.set_page_config(page_title='Registration')
st.subheader('Registration Form')

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("https://media.gettyimages.com/id/1148192366/video/hot-steel-billets-being-stacked-at-a-steel-factory.jpg?s=640x640&k=20&c=Rlrqq7hr6PCFik0kRkrXa7PXTHn9xYcS3lfuRMEAV_I=");
             background-attachment: fixed;
             background-size: cover
             
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url() 


url='data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAPDxIQEA8QEBASERAQEBUVFw8QEhcVFxEXGBYVFxMYHSkgGRolGxUVJDEiJSkrMDEyFyAzODMtNygtLisBCgoKDg0OGxAQGi4lICYrLysxMi0tLS0tMi0wNS0tNS0tLy0tLS0tLS0tLS8tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAHIBuwMBIgACEQEDEQH/xAAcAAEAAQUBAQAAAAAAAAAAAAAAAQIEBQYHCAP/xABDEAACAQMBBgMEBggBDQAAAAAAAQIDBBEFBhITITFBB1FhFCJxgSMyUnSxwRUkNUKRobLwMxYlNDZDYnJzhKLD0uH/xAAZAQEBAQEBAQAAAAAAAAAAAAAAAQQCAwX/xAAmEQEAAgEEAgICAwEBAAAAAAAAARECAxIhMQRBImEUgVFx0cET/9oADAMBAAIRAxEAPwDuIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABDJIYEAArlORkgZCqgU5GSCoFIBarJGSAUtORkgATkZIAE5GSABORkgATkgAATkgATkZIAE5GSABORkgATkEACoAEUAAAAAAAAAAAAAAAAAAAAAAAAAAAAACGSQwIAPnXqxhGUpNKMU3Jvoku5XLCba7Rw021lWeHUfuUY/an6+i6swmxviNb3rjSr4t7jksN/Rzf+7Lz9Gcp272mlqV26ib4EMwt480t37fxl1MdoOlu6rKPPcj71SXkvyZtx8aNny7ZMvInf8AHp6Q13VqVlb1Lis8Qpxz6t9or1bOa7M+K8uI4X0EoSm3GcF9RN8oyXdLpn0NV292rleunb08xt7dKOM535pYcvgl0Nb02xncVY0odZPm/Jd2XT8aNvzTU153fF6dp6jRlR9ojVg6O4576a3d1LLeTRdF8VrWtXnTrQdCm5tUaj5px7b6/db6mj7T7QcGzjpNviNKLzWkusueVDC9ebNNpUpTkoxTbk0kvPPYmHjRU7v0ufkTcU9XU6kZJSi1JNZTXNNfEqNM8MbZ0LR27nKbhJSeXlLeXNLPRZTNzMmeO3KYasZ3RaMk5PMW09WXt10lOeOPV/el9pmd231aVW10yKk+Vq5Sw2nlNR5tfA9/xp457eH5Ec8dO/5KKleEWlKcYt9E2k38MnFfC7Up29pq9dSblSoW84bzcuaVxjq/NI17Q9KnqSva9a4q8ShR9oy/fc5c+Tb6Ll2J+PzNzxC/+3EVHb0dknJxnwq1mtOhfWs6kp0427rUlJuW7yakk325rl5mC8LKsneVVKUn+oXT5uT54hz5vqSfHmN3PSxrRNcdvQWScnAPCGpKWqU05Sf0Nbq5PnuerPnshUl+n6K3pY9ruFjek19WpjkWfHqZ56i0jXuuO5eg8kZPOeoarO11qvXU5JUtQryazJrdVeSksZ5+7kze01zv7SW7jKW5K605rm0sSnDsPx5/n1ZGvH8e6dyyRlHnrbxSnrdemqk4qdejDk3y3oQWcZ9Sm89p0XU1Sp3VSfDnSbeWozjLD3ZQy10ZY8e4jn1ZOvz09D5GTg/jHXktTypSS9loSwm13qG07G7HXFjSuLqrcRqQrWM0op1G03iSbb9E1yOJ0qxjK+3Uat5TFdOn5JyeZtldJqX8qlNXEqbp286+cyknuJe715Zybt4Ka1XdxVtZ1JTpSpOrFSbluyjJJ7rfRNPp6HWfj7Ymb6c461zEV27GADO9xlvKs3UUI9vem/LyXxKrqtuR5Lek3iEemZeX9+RFpR3I83mT5zl03pYw3/JfwQFwiQCOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIZJEmBBybxj2r5fo6jLqlK6kvLrGl8+Tfphdzd9uNpoabaSq8nVlmFCPnN9HjyXU85XFaVScqlSTnOcpTnJ9XJvLb/AImvxtLdO6emXyNSo2wphBykoxWZNpJLu32Nq1KqtPtY2sH+sVVvVZLsny/+I+WzlrG2pSvqy6LFGPdvzXqzXru5lWqSqTeZTeX5eiXolyN3csfUPibfbQWm2jqzX6zWWIr7K7L5dWWGymmRnJ3NZJUaOZe90cl+SMdrepyuq0qjyo/Vpp9o56/F9WSeSOFlUk23Jttttt92zcNitIwvaZrm8ql8O8jA7P6U7qsovKpx96q/Tss+bOu7O6Vx6iju4pU8ZS6YX1Yo51M4xh1p4XLP7H2EoQlVllcRJJeifX+ZsaIjFJJLklyRJ8zLLdNvo4xUU8231q62qXNNJtupd4XfKpzkvwLDS4SuMqTzGjbVZR9EsfnI23Z20qf5RZdOoou4u/ecZqOHRqr62Md0WeyGjTS1NypTXCtKtOOYzWW6mPd5c/qrofQ3xEfqGHZMz+5V7C/szW/u1t/5yrw3/wBH1X7l/wC5kPC7Sata01ag6c4SrULeEN+MoZliv5rza/ia5ouo1NMV5Qr29VVLij7OljdxJZ58+q59iTzOUR9f8WONsz9sp4S/4t79xqfiars/YXFxNwtW1UVGdSWJcP6OKW9z+a5HQPCrQ61Ohe3VSnKEZ27o0t5NOXJuTSfPHIwnhbbVIXlVypVIr2C6S3oTis4hy5rqJziJzmCMLjGJ+0eED/zrT/5Nf+g+Wx3+sFH73cf01C58I7WpDU6TnTqRXBrLMozivqdMtHz2Qtai16jJ0qij7XXeXCajjdqYecYwM5i8v6/0xiax/thto7aVXU76ME5S9rvJY9FVk2Rs9cSq6lYym3KXtljHL64VeCX8ja9n7GUtpK+/Snw5XN8m3GSjiU5fvNY6MwWn6PVt9ZoUuFU3aWo26T3ZuO6rmDT3sYxjv6HW+Kr6c7JuJ+1xtn+36v3q2/CmVeKH7Zqf9N/REjbqlVjrVeqqNWajXpT5Rm092MHjeS9C31L2rVtSVVWtWDq1KUVHdniMY4WXJpLomyY9Yz9f4uXuPtfeMLX6Rjnp7Hb5/wC83LY201WnbXMr6o5W7s/1ZOUJY919kvs4NT8YLOpLUsRp1Jx9loRzGE5Lk555pGy7I7XXd3CraVrXhQp2NVxmlVTlKKhFLEljLUn/AAPLK50op641GpNubbJ2l3WlUjZ1FCatqkquXu5pJLeinh9TefBCta8arDhzV3w877eYOnvc4pdmvdMN4V21SFxcOVOpFOwrrnCcee6uWWi88GbapDUZOVOpBez1FmUZRX1o8stfE71puMoeenFTjLt5EngktLh78lSXT61T/h+z8/wPntyLdcSXEfTDVNend/MvEimMcdOhUBUACOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIkGQBxjxf0e+ncO5ceLaQilDc60l+85x6833NG2f0t3VZR/2cfeqS7JZ6fM9L3FPv6YNH1TRaVK43belGnx8TaisJzy03jt8Ohu0dX47WDV0/lbWNc2Sr3tBStZJ8DlwHiO8scnGXn6M0Gz0urUuPZ3CUKieKiknGUEurafQ9JadpUaFJRjzl9ab7t4MHtXZR9yqoR4ueG5YW84vpFvvzRcNe5oz0aaBregXM7Ph2cOJTpYdWEX9LJeaj+8vNdTn1KlKc1CKbm5bqXPOfX1PSmiaTwKOWvpJYlL08omD2p0O331eKjBXCajKa5Np932z6lw17mkz0qavs7o/BhCjTW9UlJbz85Pr8kdT0rT429JQj16yfnLuzD7JaVuR48170liHpHz+Zspn19TdNNOlhUWAA8Hqp3V5Ixt/qio1qdLh7yqP6SSaSgm8RbXfMuXzMoYW+2epV3WlVzKc0o05JzjuKK9zknhtS55+BYr2k36ZdRS6Y/D++5iPaqlX6SNrSqUlNxi5SiqjSluykouOEk88m+eDLUYtRSk95pJN9MvHUwd7s9KpF0XOk7dynJKVNTqQ3nmXDm3hdXh45ZJBLPJGE0nWePNJK1im5pxjWUqyUZNc6e76eZmoxwsGK0zTa9FxjxKMqac3hU2p4bb+vvevkWKJXmo1+DRnVUN+UIuSisJyflkt7PU4VZUlGGOJCpN55ODg4xlBr7ScsfIu7+141KVPO7vLGeuPUtKekKN0rhVJYdKUJQ5brk3H6T0eIJMRVE3fD76ldcGG8ob8nKMIR5RzKTwk5dl6kWdSrKUlVoxg1uuMoyU4Sz6tJprHdeXMr1G040N1S3JKUZwljOJReVy7r0KbK3qxcpVqqm3hJRjuQilnmk23vPPN58iel9qrmuoTpx3U+JJxzy5Yi3n+RTqlyrehVrYj9FTnUw3uR92LfOXZep9Li13505Zxw5OXxzFr8yNUtXWoVaSai6lOcE2spb0Wua7jgW2mXrruWXbSSx/hVeM18fdWCnXNTVpTjNxhiVSNNzk+HSgpJ+9UqYe7HKSz5yiu597C3rxk3VnRkmljcg6bz6tyeSu/oVJxXCqcOcZb3OKnGSw04yXXHPs08pduTvFp6U6bXlUhvSpwi84ThKNSEl9qM1jKfwLtRXkiy0jT+BGWdzenNzluR4cMvriOeX5l82RYfK5r7kc4y3yiumZdl6fEi1pbq5vMm25vpl/3ywUUVxJcR9Fypr8ZF0kAJSCJIoAAoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAhkEsYCIPg7SHEVTHvRi4r5tP8AIuMDBbKQfKrbwnjeinhqS+K7n2wMBKQW93ZwqrdksrKb+TyXJAiaKvtCWOnQkAKAnAwBAJwTggpwTgkBVOBgqARGCMFQCowMEgCMDBIAjBGCoAU4PnWpbyxnCys/Duj7DAFMVhYXToiUSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//Z'

st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] + div {{
                position:relative;
                bottom: 0;
                height:50%;
                background-image: url({url});
                background-size: 85% auto;
                background-repeat: no-repeat;
                background-position-x: center;
                background-position-y: bottom;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

## Initialize registration form
registration_form = face_rec.RegistrationForm()


# Step 1: Collect person name and role
  #Form
person_name = st.text_input(label= 'Name', placeholder='First & Last Name')
role = st.selectbox(label='Select your role', options = ('Worker', 'Admin Staff'))


#Step 2: Collect facial embeddings
def video_callback_func(frame):
    img = frame.to_ndarray(format='bgr24') #nd stands for n dimension array
    reg_img, embedding = registration_form.get_embedding(img)
    #two step process
    # step 1: save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt', mode='ab') as f:
            np.savetxt(f,embedding)
    
    return av.VideoFrame.from_ndarray(img,format='bgr24')

webrtc_streamer(key='registration',video_frame_callback=video_callback_func)


#Step 3: Save in redis database
if st.button('Submit'):
    return_val = registration_form.save_data_in_redis_db(person_name, role)
    if return_val == True:
        st.success(f"{person_name} registered successfully")
    elif return_val == 'name_false':
        st.error('Please enter the name: name cannot be empty or spaces')
    elif return_val == 'file_false':
        st.error('face_embedding.txt is not found. Please refresh and try again.')

        



