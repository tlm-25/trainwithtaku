
import ArticleCard from "../src/components/blogs/ArticleCard" 
import ArticleSearchCardContainer from "../src/components/blogs/ArticleSearchCardContainer"
import ArticleSearchBar from "../src/components/blogs/ArticleSearchBar"
import Layout from "../src/components/Layout"
function Blog() {


    return (
        <>

        <Layout>
            <ArticleSearchBar/>
            <ArticleSearchCardContainer/>
        </Layout>
        
        </>
    )
}
export default Blog;