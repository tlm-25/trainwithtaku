import {useState, useEffect} from 'react';





function CreateBlog(){


    return (
     <>       
        
        <div className="create-blog-container">
            <h1>Create post</h1>
            <div className="input-group">
                <label>Title: </label>
                <input placeholder='Title...' />

            </div>
            
            <div className="input-group">
                <label>Blog Content</label>
                <textarea placeholder='Post....' />
                
            </div>
            <button>Submit post</button>
        
        </div>
    </>
    

    )

}

export default CreateBlog;