const list = document.getElementsByClassName("issue list")[0];

const log = console.log

if (!list) {
    log("No gitea page..")
} else {

    const elements = list.querySelectorAll("li");

    elements.forEach((item, index) => {

        const link = item.getElementsByClassName("title")[0]

        const url = link.protocol + "//" + link.hostname + "/api/v1/repos" + link.pathname

        log("Previewing %s", url)

        fetch(url).then(response => response.json())
            .then(data => {
                let issueBody = data.body;

                const limit = 500;
                if (issueBody.length > limit) {
                    issueBody = issueBody.substr(0, limit) + "..."
                }

                issueBody = ": " + issueBody

                issueBody = check(issueBody)

                const desc = item.getElementsByClassName("desc issue-item-bottom-row df ac fw my-1")[0]

                desc.innerHTML += issueBody

            });

    });
}

/**
 * @param str
 * @returns {string|*}
 */
function check(str) {

    // remove tags
    str = str.replace(/<.*?>/, "")

    const filter = [";", "\'", "(", ")", "src", "script", "&", "|", "[", "]"]

    for (const i of filter) {
        if (str.includes(i))
            return ""
    }

    return str

}