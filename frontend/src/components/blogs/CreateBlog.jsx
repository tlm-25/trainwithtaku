import {useState, useEffect, useRef} from 'react';
import {toast} from 'react-hot-toast';
import {BASE_URL} from '../../api';

function CreateBlog(){
    const [title, setTitle] = useState("");
    const [postText, setPostText] = useState("");
    const [headlineImageFile,setHeadlineImageFile] = useState(null);

    const fileRef = useRef(null); 

    function resetInputs(){
        setTitle("");
        setPostText("");
        setHeadlineImageFile(null)
    }


    const  handleUploadBlog = async (event) => {
        // stop the form refreshing page once the form is submitted
        event.preventDefault(); 

        const formData = new FormData();
        formData.append('title',title);
        formData.append('article_text',postText);

        if(headlineImageFile){
            formData.append('headline_image_file',headlineImageFile)
            


        }

        try {
            const response = await fetch(`${BASE_URL}/api/upload_blog`,{
                method: 'POST',
                body: formData
            })

            const data = await response.json()

            if (response.ok){
                toast.success(data.message);
            }
            else {
                toast.error(data.message || "Failed to upload post. Please try again.");
            }
        }
        catch (error) {
            toast.error("Failed to upload post. Please check your connection and try again.");
        }

        resetInputs();

    }

    const handleFileInputChange = async (event) => {
        /**
         *Placeholder for image file upload
         */
        setHeadlineImageFile(event.target.files[0])




    }


    return (
     <>       
        
        <form className="create-blog-container" onSubmit={handleUploadBlog}>
            <h1>Create post</h1>
            <div className="input-group">
                <label>Title: </label>
                <input placeholder='Title...' onChange={(e)=>{setTitle(e.target.value)}}/>

            </div>
            
            <div className="input-group">
                <label>Blog Content</label>
                <textarea placeholder='Post....' onChange={(e)=>{setPostText(e.target.value)}}/>      
            </div>

            <input type ="file" accept=".jpg, .jpeg, .png, .tif, .tiff, " onChange={handleFileInputChange}/>

            {headlineImageFile && <p>Selected file: {headlineImageFile.name}</p>}
            <button type="submit">Submit post</button>
        
        </form>
    </>
    

    )

}

export default CreateBlog;