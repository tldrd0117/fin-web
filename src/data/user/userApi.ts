

const url = process.env.NODE_ENV=="production"?"/user/":"http://localhost:8083/user/"

const BASEURL = url;

const commonHeader = {
    "Content-Type": "application/json",
    "Authorization": "application/json",

}


export const getToken = async (username: string, password: string) => {
    const formData = new FormData()
    formData.append("username", username);
    formData.append("password", password);
    try{
        const response: Response = await fetch(`${BASEURL}token`,{
            method: "POST",
            body: formData
        })
        const json = await response.json()
        return {response: json}
    } catch(e){
        console.log(e)
        return {error: e};
    }
}

export const getMe = async (token: string) => {
    const response: Response = await fetch(`${BASEURL}me`,{
        body: JSON.stringify({
            token
        })
    })
    return await response.json()
}
