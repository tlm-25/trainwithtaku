import {useState, useEffect, useRef} from 'react';

function CreateBlog(){
    const [title, setTitle] = useState("");
    const [postText, setPostText] = useState("");
    const [headlineImageFile,setHeadlineImageFile] = useState(null);

    const fileRef = useRef(null); 


    const  handleUploadBlog = async (event) => {
        // stop the form refreshing page once the form is submitted
        event.preventDefault(); 

        const formData = new FormData();
        formData.append('headline',title);
        formData.append('article_text',postText);
        formData.append('upload_date',new Date().toISOString());
        if(headlineImageFile){
            formData.append('headline_image_file',headlineImageFile)


        }
        
       

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