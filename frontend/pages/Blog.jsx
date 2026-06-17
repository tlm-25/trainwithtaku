
import ArticleCard from "../src/components/blogs/ArticleCard" 
import ArticleSearchBar from "../src/components/blogs/ArticleSearchBar"
import Layout from "../src/components/Layout"
function Blog() {


    return (
        <>

        <Layout>
            <ArticleSearchBar/>
            <ArticleCard/>
        </Layout>
        
        </>
    )
}
export default Blog;