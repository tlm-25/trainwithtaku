import { useState, useEffect } from "react"


function ArticleSearchBar() {

    const [searchInput,setSearchInput] = useState("")




    return (
        <>

        <div className="search-bar-container">
            <input type="text" placeholder="Search article" onChange={(e)=>setSearchInput(e.target.value)}/>
            <button>Search</button>
        </div>
        </>
    )
}

export default ArticleSearchBar