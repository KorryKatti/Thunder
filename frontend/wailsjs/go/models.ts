export namespace main {
	
	export class IndexEntry {
	    name: string;
	    full_name: string;
	    repo: string;
	    url: string;
	    dir_name: string;
	    entry_point: string;
	    description: string;
	    installed_at: string;
	
	    static createFrom(source: any = {}) {
	        return new IndexEntry(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.full_name = source["full_name"];
	        this.repo = source["repo"];
	        this.url = source["url"];
	        this.dir_name = source["dir_name"];
	        this.entry_point = source["entry_point"];
	        this.description = source["description"];
	        this.installed_at = source["installed_at"];
	    }
	}
	export class ProjectInfo {
	    has_pyproject: boolean;
	    has_requirements: boolean;
	    project_name: string;
	    entry_point: string;
	    language: string;
	    file_name: string;
	    file_size: number;
	
	    static createFrom(source: any = {}) {
	        return new ProjectInfo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.has_pyproject = source["has_pyproject"];
	        this.has_requirements = source["has_requirements"];
	        this.project_name = source["project_name"];
	        this.entry_point = source["entry_point"];
	        this.language = source["language"];
	        this.file_name = source["file_name"];
	        this.file_size = source["file_size"];
	    }
	}
	export class RepoInfo {
	    Name: string;
	    FullName: string;
	    Description: string;
	    Stars: number;
	    Forks: number;
	    Language: string;
	    LicenseName: string;
	    URL: string;
	    DefaultBranch: string;
	
	    static createFrom(source: any = {}) {
	        return new RepoInfo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Name = source["Name"];
	        this.FullName = source["FullName"];
	        this.Description = source["Description"];
	        this.Stars = source["Stars"];
	        this.Forks = source["Forks"];
	        this.Language = source["Language"];
	        this.LicenseName = source["LicenseName"];
	        this.URL = source["URL"];
	        this.DefaultBranch = source["DefaultBranch"];
	    }
	}

}

